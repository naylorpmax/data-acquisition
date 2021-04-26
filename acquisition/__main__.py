import os
import time
from typing import List, Tuple

import pandas as pd
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

from .network import Network
from .artist import Artist


def main():
    vertices_path = os.environ.get("VERTICES_PATH")
    edges_path = os.environ.get("EDGES_PATH")
    playlists_path = os.environ.get("PLAYLISTS_PATH")

    spotify = Spotify(auth_manager=SpotifyClientCredentials())
    audio_features = [
        "danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness",
        "liveness", "valence", "tempo", "duration_ms", "time_signature"
    ]

    if vertices_path and edges_path:
        print("Loading graph from file")
        vertices = pd.read_csv(vertices_path)
        edges = pd.read_csv(edges_path)

        network = Network.from_dataframe(spotify=spotify, audio_features=audio_features,
                                         max_tracks=50, vertices=vertices, edges=edges)
        print(f"Loaded {len(network.graph.nodes)} nodes and {len(network.graph.edges)}")
    else:
        network = Network(spotify=spotify, audio_features=audio_features, max_tracks=50)

    print("Adding new tracks and artists via seed playlists")
    playlist_names = read_lines(playlists_path)
    for name, playlist_id in playlist_names:
        start_time = time.time()
        playlist = network.get_playlist(playlist_id=playlist_id)
        if not playlist:
            continue

        print(f"Exploring via playlist: {playlist.name} ({playlist.id})")
        add_artists(network, playlist.get_artists(), 0, 2)

        print(f"Writing {len(network.graph.nodes)} nodes and {len(network.graph.edges())} edges to file")
        vertices, edges = network.graph.to_dataframe()
        vertices.to_csv(f"vertices_{name}.csv", index=False)
        edges.to_csv(f"edges_{name}.csv", index=False)
        print(f"Completed: {time.time() - start_time}")


def add_artists(network: Network, seed_artists: List[Artist], curr_depth: int, max_depth: int):
    if curr_depth == max_depth or len(seed_artists) <= 0:
        return

    unseen_seed_artists = network.graph.get_unseen_artists(seed_artists)
    print(f"{len(unseen_seed_artists)} unseen artists in layer {curr_depth} of network")

    next_seed_artists = []
    for seed_artist in unseen_seed_artists:
        next_seed_artists += add_artist(network, seed_artist)

    add_artists(network, next_seed_artists, curr_depth+1, max_depth)


def add_artist(network: Network, seed_artist: Artist):
    found_tracks = network.search_tracks(seed_artist.name)
    top_tracks = network.get_top_tracks(seed_artist, True)
    network.put_audio_features([tup[0] for tup in found_tracks + top_tracks])

    related_artists = network.get_related_artists(seed_artist)
    collaborators = {}
    for track, artists in found_tracks + top_tracks:
        network.graph.put_track(track, artists)
        for artist in artists:
            collaborators[artist.name] = artist

    unseen_associated_artists = network.graph.get_unseen_artists(related_artists + list(collaborators.values()))
    print(
        f"Tracks: {len(found_tracks + top_tracks)}\t",
        f"Associated artists: {len(unseen_associated_artists)}\t",
        f"Artist: {seed_artist.name}"
    )

    return unseen_associated_artists


def read_lines(path: str) -> List[Tuple[str, str]]:
    with open(path) as f:
        lines = f.readlines()
    return [(line.split("|")[0].strip(), line.split("|")[1].strip()) for line in lines]


if __name__ == '__main__':
    main()
