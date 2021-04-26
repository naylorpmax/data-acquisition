from typing import Any, Dict


class Track:
	def __init__(self, name: str, track_id: str, album: str, album_type: str, attr: Dict[str, Any] = None):
		self.attr = {}
		if attr:
			self.attr = attr

		self.id = track_id
		self.name = name
		self.album = album
		self.album_type = album_type
		self.node_type = 'track'

	def set_attrs(self, attrs: Dict[str, Any]):
		self.attr = attrs

	def __eq__(self, other):
		return self.id == other.id \
			and self.name == other.name \
			and self.album == other.album \
			and self.album_type == other.album_type

	def __hash__(self):
		return hash(('id', self.id, 'name', self.name))
