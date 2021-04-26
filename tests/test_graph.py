import random

from pandas import DataFrame

from acquisition.graph import Graph
from acquisition.track import Track
from acquisition.artist import Artist

tracks = [
    (
        Track(track_id="000", name="Diddy Bop", album="Telefone", album_type="album"),
        [
            Artist(artist_id="0001", name="Noname"),
            Artist(artist_id="0002", name="Cam O'bi"),
            Artist(artist_id="0003", name="Raury")
        ]
    ),
    (
        Track(track_id="111", name="Yesterday", album="Telefone", album_type="album"),
        [Artist(artist_id="0001", name="Noname")]
    ),
    (
        Track(track_id="222", name="Forever", album="Telefone", album_type="album"),
        [
            Artist(artist_id="0001", name="Noname"),
            Artist(artist_id="2222", name="Joseph Chilliams"),
            Artist(artist_id="2223", name="Ravyn Lenae")
        ]
    )
]


class TestGraph:
    def test_put_track(self):
        graph = Graph()
        track, artists = tracks[0]
        nodes = ["000", "0001", "0002", "0003"]         # track ID and all artist IDs
        edges = [("000", "0001"), ("000", "0002"), ("000", "0003")]     # track has edge to each artist

        # graph contains no nodes or edges
        assert [] == list(graph.nodes)
        assert [] == list(graph.edges)

        # put track; graph contains correct nodes and edges
        graph.put_track(track, artists)
        assert sorted(nodes) == sorted(list(graph.nodes))
        assert sorted(edges) == sorted(list(graph.edges))

        # put same track; graph contains same nodes and edges
        graph.put_track(track, artists)
        assert sorted(nodes) == sorted(list(graph.nodes))
        assert sorted(edges) == sorted(list(graph.edges))

    def test_to_dataframe(self):
        # setup
        expected_vertices = DataFrame({
            "id": ["000", "111", "222", "0001", "0002", "0003", "2222", "2223"],
            "name": ["Diddy Bop", "Yesterday", "Forever", "Noname", "Cam O'bi", "Raury", "Joseph Chilliams", "Ravyn Lenae"],
            "album": ["Telefone", "Telefone", "Telefone", None, None, None, None, None],
            "album_type": ["album", "album", "album", None, None, None, None, None],
            "node_type": ["track", "track", "track", "artist", "artist", "artist", "artist", "artist"]
        })

        expected_edges = DataFrame({
            "source": ["000", "000", "000", "111", "222", "222", "222"],
            "target": ["0001", "0002", "0003", "0001", "0001", "2222", "2223"],
        })

        graph = Graph()
        for track, artists in tracks:
            graph.put_track(track, artists)

        # run test
        vertices, edges = graph.to_dataframe()

        assert expected_vertices.equals(vertices)
        assert expected_edges.equals(edges)

    def test_unseen_artists(self):
        # setup
        graph = Graph()
        for track, artists in tracks:
            graph.put_track(track, artists)

        expected = [
            Artist(artist_id="0002", name="Cam O'bi"),
            Artist(artist_id="0003", name="Raury"),
            Artist(artist_id="2222", name="Joseph Chilliams"),
            Artist(artist_id="2223", name="Ravyn Lenae")
        ]

        # run test
        assert expected == sorted(graph.get_unseen_artists([
            Artist(artist_id="0001", name="Noname"),
            Artist(artist_id="0002", name="Cam O'bi"),
            Artist(artist_id="0003", name="Raury"),
            Artist(artist_id="2222", name="Joseph Chilliams"),
            Artist(artist_id="2223", name="Ravyn Lenae")
        ]), key=lambda a: a.id)
