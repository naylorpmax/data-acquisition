from typing import List, Tuple

from graph.artist import Artist
from graph.track import Track


class Playlist:
	def __init__(self, playlist_id: str, name: str, entries: List[Tuple[Track, List[Artist]]]):
		self.id = playlist_id
		self.name = name
		self.entries = entries

	def get_artists(self):
		temp = []
		for track, artists in self.entries:
			temp += artists
		return list(set(temp))
