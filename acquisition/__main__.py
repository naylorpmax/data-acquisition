import json, os, datetime
from typing import List, Tuple

from .spotifynetwork import Track, Network, Artist

import networkx as nx
import pandas as pd


def read_lines(path: str) -> List[Tuple[str, str]]:
	with open(path) as f:
		lines = f.readlines()
	return [(line.split("|")[0].strip(), line.split("|")[1].strip()) for line in lines]


def main():
	network = Network(
		audio_features=["danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature"],
		max_tracks=50
	)

	playlist_names = read_lines(os.environ["PLAYLIST_PATH"])
	for name, playlist_id in playlist_names:
		start_time = datetime.datetime.now()
		playlist = network.get_playlist(playlist_id=playlist_id)
		print(f"Exploring via playlist: {playlist.name} ({playlist.id})")
		add_artists(network, playlist.get_artists(), 0, 2)

		V, E = network.to_dataframe()

		print(f"Writing {len(network.graph.nodes())} nodes and {len(network.graph.edges())} edges to file")
		V.to_csv(f"vertices_{name}.csv", index=False)
		E.to_csv(f"edges_{name}.csv", index=False)
		print(f"Completed: {datetime.datetime.now() - start_time}")


def add_artists(network: Network, seed_artists: List[Artist], curr_depth: int, max_depth: int):
	if curr_depth == max_depth or len(seed_artists) <= 0:
		return

	unseen_seed_artists = network.unseen_artists(seed_artists)
	print(f"{len(unseen_seed_artists)} unseen artists in layer {curr_depth} of network")
	
	next_seed_artists = []
	for seed_artist in unseen_seed_artists:
		found_tracks = network.search_tracks(seed_artist.name)
		top_tracks = network.top_tracks(seed_artist, True)
		network.get_audio_features([tup[0] for tup in found_tracks + top_tracks])

		related_artists = network.related_artists(seed_artist)
		collaborators = {}
		for track, artists in found_tracks + top_tracks:
			network.put_track(track, artists)
			for artist in artists:
				collaborators[artist.name] = artist

		unseen_associated_artists = network.unseen_artists(related_artists + list(collaborators.values()))
		next_seed_artists += unseen_associated_artists
		print(f"Tracks: {len(found_tracks + top_tracks)}\tAssociated artists: {len(unseen_associated_artists)}\tArtist: {seed_artist.name}")

	add_artists(network, next_seed_artists, curr_depth+1, max_depth)


if __name__ == '__main__':
	main()
