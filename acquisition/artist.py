from typing import Any, Dict


class Artist:
	def __init__(self, artist_id: str, name: str, attr: Dict[str, Any] = None):
		self.attr = {}
		if attr:
			self.attr = attr

		self.id = artist_id
		self.name = name
		self.node_type = 'artist'

	def __eq__(self, other):
		return self.id == other.id and self.name == other.name

	def __hash__(self):
		return hash(('id', self.id, 'name', self.name))
