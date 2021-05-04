from typing import Any, Dict, List


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

	@classmethod
	def from_response(cls, response: Dict[str, Any], keys: List[str], seen: bool = False):
		attr = {}
		for k in keys:
			attr[k] = response.get(k)

		if seen:
			attr['seen'] = seen

		return cls(artist_id=response['id'], name=response['name'], attr=attr)

	def with_attrs(self, attrs: Dict[str, Any]):
		self.attr = attrs
		return self
