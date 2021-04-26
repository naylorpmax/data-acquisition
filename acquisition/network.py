import json
import traceback
from typing import Any, Dict, List, Tuple, Union

from spotipy import Spotify
import networkx as nx
import pandas as pd

from .artist import Artist
from .graph import Graph
from .playlist import Playlist
from .track import Track


class Network:
	def __init__(self, spotify: Spotify, audio_features: List[str], max_tracks: int, graph: nx.Graph = None):
		self.graph = Graph(graph)
		self.spotify = spotify
		self.audio_features = audio_features
		self.max_tracks = max_tracks

	# TODO: test this
	@classmethod
	def from_dataframe(
			cls,
			spotify: Spotify,
			audio_features: List[str],
			max_tracks: int,
			vertices: pd.DataFrame,
			edges: pd.DataFrame
	):
		graph = Graph(nx.from_pandas_edgelist(edges))
		records = vertices.to_dict('records')
		for record in records:
			attr = {}
			for k, v in record.items():
				if 'attr' in k:
					attr[k.replace("attr.", "")] = v

			if record['node_type'] == 'track':
				graph.add_track(Track(
					track_id=record['id'],
					name=record['name'],
					album=record['album'],
					album_type=record['album_type'],
					attr=attr
				))
			elif record['node_type'] == 'artist':
				graph.add_artist(Artist(
					artist_id=record['id'],
					name=record['name'],
					attr=attr
				))
			else:
				print("weird node found; skipping")
				continue

		return cls(graph=graph, spotify=spotify, audio_features=audio_features, max_tracks=max_tracks)

	# TODO: test this
	def search_tracks(self, artist_name: str, seen: bool = False) -> List[Tuple[Track, List[Artist]]]:
		tracks = {}
		limit = 50
		offset = 0
		total = 1
		while offset <= total and offset <= self.max_tracks:
			try:
				results = self.spotify.search(artist_name, type='track', limit=limit, offset=offset)
			except Exception as e:
				print(
					f"exception while searching, skipping batch of tracks:\n",
					format_traceback(e)
				)
				offset += limit
				continue

			offset += limit
			total = results['tracks']['total']

			if 'artists' not in results['tracks']['items']:
				continue

			for result in results['tracks']['items']:
				if artist_name in [artist['name'] for artist in result['artists']]:
					tracks[result['name']] = (
						self.track_from_response(result),
						[self.artist_from_response(artist, seen) for artist in result['artists']]
					)

		return list(tracks.values())

	def get_top_tracks(self, artist: Artist, seen: bool = False) -> List[Tuple[Track, List[Artist]]]:
		try:
			results = self.spotify.artist_top_tracks(artist.id)
		except Exception as e:
			print(
				f"exception while getting top tracks, skipping artist ({artist.name}):\n",
				format_traceback(e)
			)
			return []

		tracks = {}
		for result in results['tracks']:
			tracks[result['name']] = (
				self.track_from_response(result),
				[self.artist_from_response(artist, seen) for artist in result['artists']]
			)

		return list(tracks.values())

	def get_related_artists(self, artist: Artist, seen: bool = False) -> List[Artist]:
		try:
			results = self.spotify.artist_related_artists(artist.id)
		except Exception as e:
			print(
				f"exception while getting related artists, skipping artist ({artist.name}):\n",
				format_traceback(e)
			)
			return []

		if not results['artists']:
			return []
		return [self.artist_from_response(artist, seen) for artist in results['artists']]

	def put_audio_features(self, tracks: List[Track]):
		n = 100
		batches = [tracks[i * n:(i+1) * n] for i in range((len(tracks) + n-1) // n)]

		for batch in batches:
			tracks_map = {}
			for track in batch:
				tracks_map[track.id] = track

			try:
				results = self.spotify.audio_features(tracks_map.keys())
			except Exception as e:
				print(
					f"exception while getting audio features, skipping batch of tracks:\n",
					format_traceback(e)
				)
				continue

			if len(results) <= 0:
				continue

			for result in results:
				if not result:
					continue

				track_id = result['id']
				if track_id not in tracks_map:
					continue

				audio_features = {}
				for name in self.audio_features:
					audio_features[name] = result.get(name)
				tracks_map[track_id].set_attrs(audio_features)

	# TODO: test this
	def get_playlist(self, playlist_id: str) -> Union[Playlist, None]:
		try:
			playlist = self.spotify.playlist(playlist_id=playlist_id)
		except Exception as e:
			print(
				f"exception while getting playlist, skipping playlist ({playlist_id}):\n",
				format_traceback(e)
			)
			return

		playlist_name = playlist['name']
		total_tracks = playlist['tracks']['total']

		entries = {}
		offset = 0
		limit = 50
		while offset <= total_tracks:
			results = self.get_playlist_tracks(playlist_id, offset, limit)
			offset += limit

			if not results:
				continue
			if len(results['items']) <= 0 or not results['items'][0]:
				break

			for result in results['items']:
				if not result['track']:
					continue
				track = result['track']
				entries[track['name']] = self.track_with_artists_from_response(result['track'])

		return Playlist(
			playlist_id=playlist_id,
			name=playlist_name,
			entries=list(entries.values())
		)

	# TODO: test this
	def get_playlist_tracks(self, playlist_id: str, offset: int, limit: int) -> Dict[str, Any]:
		try:
			return self.spotify.playlist_tracks(playlist_id=playlist_id, offset=offset, limit=limit)
		except Exception as e:
			print(
				f"exception while getting playlist tracks, skipping batch of tracks ({playlist_id}):\n",
				format_traceback(e)
			)
			return {}

	def track_with_artists_from_response(self, response: Dict[str, Any]):
		return (
			self.track_from_response(response),
			[self.artist_from_response(artist) for artist in response['artists']]
		)

	def artist_from_response(self, response: Dict[str, Any], seen: bool = False) -> Artist:
		attr = {'popularity': response.get('popularity'), 'genres': response.get('genres')}
		if seen or response['id'] in self.graph.get_node_attributes('seen'):
			attr['seen'] = True

		return Artist(artist_id=response['id'], name=response['name'], attr=attr)

	@staticmethod
	def track_from_response(response: Dict[str, Any]) -> Track:
		return Track(
			track_id=response['id'],
			name=response['name'],
			album=response['album']['name'],
			album_type=response['album']['album_type']
		)


def format_traceback(e: Exception) -> str:
	return json.dumps(traceback.format_tb(e.__traceback__), indent=3)
