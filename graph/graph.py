from typing import Dict, Any, List

import networkx as nx
import pandas as pd

from graph.artist import Artist
from graph.track import Track


class Graph:
	def __init__(self, nx_graph: nx.DiGraph = None):
		self.nx_graph = nx.DiGraph()
		if nx_graph:
			self.nx_graph = nx_graph
		self.nodes = self.nx_graph.nodes
		self.edges = self.nx_graph.edges

	def add_artist(self, artist: Artist, **attr):
		self.nx_graph.add_node(artist.id, artist=artist, **attr)

	def add_track(self, track: Track, **attr):
		self.nx_graph.add_node(track.id, track=track, **attr)

	def add_edge(self, a, b, **attr):
		self.nx_graph.add_edge(a, b, **attr)

	def get_node_attributes(self, attr_name: str) -> Dict[str, Any]:
		return nx.get_node_attributes(self.nx_graph, attr_name)

	def to_dataframe(self) -> (pd.DataFrame, pd.DataFrame):
		tracks = [track.__dict__ for track in self.get_node_attributes('track').values()]
		artists = [artist.__dict__ for artist in self.get_node_attributes('artist').values()]
		vertices = pd.json_normalize(tracks + artists)
		edges = nx.to_pandas_edgelist(self.nx_graph)
		return vertices, edges

	def get_unseen_artists(self, artists: List[Artist]) -> List[Artist]:
		unique_artists = list(set(artists))
		seen_artists = self.get_node_attributes('seen')
		return [artist for artist in unique_artists if artist.id not in seen_artists]

	def put_track(self, track: Track, artists: List[Artist]):
		if track.id in self.nodes:
			return

		self.add_track(track)
		for artist in artists:
			if artist.attr.get('seen') or artist.id in self.nx_graph.nodes:
				self.add_artist(artist, seen=True)
			else:
				self.add_artist(artist)
			self.add_edge(track.id, artist.id)
