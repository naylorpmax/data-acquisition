import json, os, datetime
from typing import List, Tuple

from .spotifynetwork import Track, Network, Artist

import networkx as nx
import pandas as pd


# def main():
# 	with open("testing.json") as f:
# 		network = nx.readwrite.json_graph.adjacency_graph(f.read())
	# print(network)

def read_lines(path: str) -> List[Tuple[str, str]]:
	with open(path) as f:
		lines = f.readlines()
	return [(line.split("|")[0].strip(), line.split("|")[1].strip()) for line in lines]

def main():
	playlist_names = read_lines(os.environ["PLAYLIST_PATH"])

	network = Network(
		audio_features=["danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature"],
		max_tracks=50
	)

	for name, playlist_id in playlist_names:
		start_time = datetime.datetime.now()
		playlist = network.get_playlist(playlist_id=playlist_id)
		print(f"Exploring via playlist: {playlist.name} ({playlist.id})")
		add_artists(network, playlist.get_artists(), 0, 2, 15)

		V, E = network.to_dataframe()

		print(f"Writing {len(network.graph.nodes())} nodes and {len(network.graph.edges())} edges to file")
		V.to_csv(f"vertices_{playlist.name}.csv", index=False)
		E.to_csv(f"edges_{playlist.name}.csv", index=False)
		print(f"Completed: {datetime.datetime.now() - start_time}")


def add_artists(network: Network, seed_artists: List[Artist], curr_depth: int, max_depth: int, max_breadth: int):
	if curr_depth == max_depth or len(seed_artists) <= 0:
		return

	print(f"{len(seed_artists)} unseen artists in layer {curr_depth} of network")
	
	associated_artists = []
	for seed_artist in seed_artists:
		found_tracks = network.search_tracks(seed_artist.name)
		top_tracks = network.top_tracks(seed_artist)
		related_artists = network.related_artists(seed_artist)
		collaborators = {}

		print(f"Added {len(found_tracks + top_tracks)} tracks by artist: {seed_artist.name}")

		for retrieved_track, retrieved_artists in found_tracks + top_tracks:
			network.put_track(retrieved_track, retrieved_artists)
			for artist in retrieved_artists:
				collaborators[artist.name] = artist

		associated_artists += list(set(related_artists + list(collaborators.values())))[:max_breadth]

	known_artists = network.graph.nodes()
	unknown_associated_artists = [artist for artist in list(set(associated_artists)) if artist.id not in known_artists]
	add_artists(network, unknown_associated_artists, curr_depth+1, max_depth, max_breadth)


if __name__ == '__main__':
	main()
