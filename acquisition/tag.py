import time, os, json
from typing import List, Dict, Any, Tuple

import asyncio, aiohttp, async_timeout
import pandas as pd
from asyncio.exceptions import InvalidStateError
from urllib.parse import quote_plus
from urllib3.exceptions import HTTPError


def main():
	start_time = time.time()
	lastfm = LastFMClient(
		client_id=os.environ["LASTFM_CLIENT_ID"],
		client_secret=os.environ["LASTFM_CLIENT_SECRET"]
	)
	
	vertices_path = os.environ["VERTICES_PATH"]

	final_vertices = []
	tag = True
	for vertices in pd.read_csv(vertices_path, chunksize=1000):
		not_artists = vertices[vertices['node_type'] != 'artist']
		if len(not_artists) > 0:
			final_vertices.append(not_artists)

		artists = vertices[vertices['node_type'] == 'artist']
		if len(artists) > 0:
			if tag:
				res = asyncio.get_event_loop().run_until_complete(tag_artists(lastfm, artists))
				if res:
					print("rate limited; not tagging the rest of the artists")
					tag = False
			final_vertices.append(artists)

	print(f"Completed: {time.time() - start_time}")
	pd.concat([df for df in final_vertices], ignore_index=True).to_csv(vertices_path, index=False)


class LastFMClient:
	def __init__(self, client_id: str, client_secret: str, base_url: str="https://ws.audioscrobbler.com/2.0/"):
		self.client_id = client_id
		self.client_secret = client_secret
		self.base_url = base_url

	async def get_top_tags(self, session: aiohttp.ClientSession, artist_index: int, artist_name: str) -> (int, Dict[str, Any]):
		params = {
			'artist': artist_name,
			'api_key': self.client_id,
			'method': 'artist.getTopTags',
			'format': 'json'
		}

		url = self.base_url + "?" + "&".join(["=".join([k, quote_plus(v)]) for k, v in params.items()])
		with async_timeout.timeout(5):
			async with session.get(url) as resp:
				try:
					res = await resp.json()
					if "toptags" in res:
						tags = {}
						for item in res["toptags"]["tag"]:
							tags[item["name"]] = item["count"]
						print(f"Tagged {artist_name} at {artist_index}")
						return artist_index, tags
					if "error" in res:
						message = res.get('message', res['error'])
						if "Rate" in message:
							raise RateLimited(message)
						else:
							raise HTTPError(message)
				except Exception as e:
					if "could not be found" not in str(e):
						raise e
		return artist_index, []


class RateLimited(Exception):
	pass


async def tag_artists(lastfm: LastFMClient, artists: pd.DataFrame) -> str:
	print(f"Adding tags for {len(artists)} artists")
	tasks = []
	rate_limited = False

	if "tags" not in artists.columns:
		artists["tags"] = pd.Series([None])

	async with aiohttp.ClientSession() as session:
		for index, row in artists.iterrows():
			if pd.notna(row['tags']):
				print(f"artist already tagged:\t{row['name']}")
				continue
			if 'name' not in row or not row['name']:
				print(f"missing artist name at:\t{index}")
				continue
			else:
				task = asyncio.ensure_future(lastfm.get_top_tags(session, index, row['name']))
				tasks.append(task)

		try:
			await asyncio.gather(*tasks, return_exceptions=False)
		except RateLimited as _:
			rate_limited = True
			for t in tasks:
				if not task.done():
					t.cancel()
		except Exception as e:
			print(f"exception while getting tags:\n{e}")

	for task in tasks:
		try:
			if not task.cancelled():
				artist_index, tags = task.result()
				if tags and artist_index:
					artists.loc[artist_index, 'tags'] = json.dumps(tags)
				else:
					artists.loc[artist_index, 'tags'] = json.dumps({'none': 0})
		except (RateLimited, InvalidStateError) as _:
			continue
		except Exception as e:
			print(f"exception while tagging artist:\n{e}")

	return rate_limited


if __name__ == '__main__':
	main()
