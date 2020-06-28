import json, os
from typing import List

import spotifynetwork as spotifynx

import networkx as nx


def main():
	network = spotifynx.Network(
		audio_features=["danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature"],
		max_tracks=150
	)

	playlist_names = []
	with open(os.environ["PLAYLIST_PATH"]) as f:
		playlist_names = f.readlines()

	output_path = os.environ["OUTPUT_PATH"]

	for name in playlist_names:
		playlist = network.get_playlist(playlist_id=name.strip())
		print(f"Exploring via playlist: {playlist.name} ({playlist.id})")
		add_artists(network, playlist.get_artists(), 0, 3, 50)

	print("Writing graph to file")
	nx.readwrite.gpickle.write_gpickle(network.graph, output_path)
	print(f"Collected {len(network.graph.nodes())} nodes and {len(network.graph.edges())} edges")


def add_artists(network: spotifynx.Network, seed_artists: List[spotifynx.Artist], curr_depth: int, max_depth: int, max_breadth: int):
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
