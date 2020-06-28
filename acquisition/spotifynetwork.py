import json
from typing import List, Dict, Any, Tuple

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import networkx as nx
import pandas as pd

class Track:
	def __init__(self, name: str, id: str, album: str, album_type: str, attr: Dict[str, Any]={}):
		self.id = id
		self.name = name
		self.album = album
		self.album_type = album_type
		self.attr = attr
		self.node_type = 'track'

	def add_attrs(self, attrs: Dict[str, Any]):
		self.attr.update(attrs)


class Artist:
	def __init__(self, id: str, name: str, attr: Dict[str, Any]={}):
		self.id = id
		self.name = name
		self.attr = attr
		self.node_type = 'artist'

	def __eq__(self, other):
		return self.id == other.id and self.name == other.name and self.attr == other.attr

	def __hash__(self):
	    return hash(('id', self.id, 'name', self.name))


class Playlist:
	def __init__(self, id: str, name: str, entries: List[Tuple[Track, List[Artist]]]):
		self.id = id
		self.name = name
		self.entries = entries

	def get_artists(self):
		temp = []
		for track, artists in self.entries:
			temp += artists
		return list(set(temp))

class Network:
	def __init__(self, audio_features: List[str], max_tracks: int):
		self.client = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
		self.graph = nx.Graph()
		self.audio_features = audio_features
		self.max_tracks = max_tracks

	def search_tracks(self, artist_name: str) -> List[Tuple[Track, List[Artist]]]:
		tracks = {}
		limit = 50; offset = 0; total = 1
		while(offset <= total and offset <= self.max_tracks):
			try:
				results = self.client.search(artist_name, type="track", limit=limit, offset=offset)
			except Exception as e:
				print(f"Exception while searching, skipping remaining tracks:\n{e}")
				break

			offset += limit
			total = results['tracks']['total']

			for result in results['tracks']['items']:
				if artist_name in [artist['name'] for artist in result['artists']]:
					tracks[result['name']] = (
					 	Track(
							id=result['id'],
							name=result['name'],
							album=result['album']['name'],
							album_type=result['album']['album_type']
						),
						[Artist(
							id=artist['id'],
							name=artist['name']
						) for artist in result['artists']]
					)

		return list(tracks.values())

	def top_tracks(self, artist: Artist) -> List[Tuple[Track, List[Artist]]]:
		results = self.client.artist_top_tracks(artist.id)
		tracks = {}
		for result in results['tracks']:
			tracks[result['name']] = (
				Track(
					id=result['id'],
					name=result['name'],
					album=result['album']['name'],
					album_type=result['album']['album_type']
				),
				[Artist(
					id=artist['id'],
					name=artist['name']
				) for artist in result['artists']]
			)

		return list(tracks.values())

	def put_track(self, track: Track, artists: List[Artist]):
		if track.id not in self.graph.nodes():
			self.add_audio_features(track)
			self.graph.add_node(track.id, track=track)
			for artist in artists:
				if artist.id not in self.graph.nodes():
					self.graph.add_node(artist.id, artist=artist)
				self.graph.add_edge(track.id, artist.id)

	def related_artists(self, artist: Artist) -> List[Artist]:
		results = self.client.artist_related_artists(artist.id)
		if results['artists']:
			return [Artist(
				id=artist['id'],
				name=artist['name']
			) for artist in results['artists']]
		else:
			return []

	def add_audio_features(self, track: Track) -> Track:
		results = self.client.audio_features(track.id)
		if len(results) <= 0 or not results[0]:
			return
		result = results[0]					# for now take the first one
		assert(result['id'] == track.id)	# checking just in case

		audio_features = {}
		for name in self.audio_features:
			audio_features[name] = result.get(name)
		track.add_attrs(audio_features)

	def get_playlist(self, playlist_id: str) -> Playlist:
		playlist = self.client.playlist(playlist_id=playlist_id)
		playlist_name = playlist['name']
		total_tracks = playlist['tracks']['total']

		entries = {}; offset = 0; limit = 50
		while(offset <= total_tracks):
			results = self.client.playlist_tracks(playlist_id=playlist_id, offset=offset, limit=limit)
			offset += limit
			if len(results['items']) <= 0 or not results['items'][0]:
				break

			for result in results['items']:
				track = result['track']
				entries[track['name']] = (
					Track(
						id=track['id'],
						name=track['name'],
						album=track['album']['name'],
						album_type=track['album']['album_type']
					),
					[Artist(
						id=artist['id'],
						name=artist['name']
					) for artist in track['artists']]
				)

		return Playlist(
			id=playlist_id,
			name=playlist_name,
			entries=list(entries.values())
		)			

	def to_dataframe(self) -> (pd.DataFrame, pd.DataFrame):
		tracks = [track.__dict__ for track in nx.get_node_attributes(self.graph, 'track').values()]
		artists = [artist.__dict__ for artist in nx.get_node_attributes(self.graph, 'artist').values()]
		V = pd.json_normalize(tracks + artists)
		E = nx.to_pandas_edgelist(self.graph)
		return V, E

	def from_dataframe(self, V: pd.DataFrame, E: pd.DataFrame):
		G = nx.from_pandas_edgelist(E)
		records = V.to_dict('records')
		for record in records:
			if record['node_type'] == 'track':
				attr = {}
				for k, v in record.items():
					if 'attr' in k:
						attr[k.replace("attr.", "")] = v

				G.add_node(record['id'], track=Track(id=record['id'], name=record['name'], album=record['album'], album_type=record['album_type'], attr=attr))
			elif record['node_type'] == 'artist':
				G.add_node(record['id'], artist=Artist(id=record['id'], name=record['name']))
			else:
				print("Weird node found; skipping")
				continue

		self.graph = G
