import copy
from unittest.mock import Mock

from graph.track import Track
from graph.artist import Artist
from graph.network import Network

tracks_response = {
    "tracks": [
        {
            "name": "Diddy Bop",
            "id": "000",
            "album": {
                "name": "Telefone",
                "album_type": "album"
            },
            "artists": [
                {
                    "id": "0001",
                    "name": "Noname"
                },
                {
                    "id": "0002",
                    "name": "Cam O'bi"
                },
                {
                    "id": "0003",
                    "name": "Raury"
                }
            ]
        },
        {
            "name": "Yesterday",
            "id": "111",
            "album": {
                "name": "Telefone",
                "album_type": "album"
            },
            "artists": [
                {
                    "id": "0001",
                    "name": "Noname"
                }
            ]
        },
        {
            "name": "Forever",
            "id": "222",
            "album": {
                "name": "Telefone",
                "album_type": "album"
            },
            "artists": [
                {
                    "id": "0001",
                    "name": "Noname"
                },
                {
                    "id": "2222",
                    "name": "Joseph Chilliams"
                },
                {
                    "id": "2223",
                    "name": "Ravyn Lenae"
                }
            ]
        }
    ]
}

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

artists_response = {
    "artists": [
        {
            "id": "0002",
            "name": "Cam O'bi"
        },
        {
            "id": "0003",
            "name": "Raury"
        },
        {
            "id": "2222",
            "name": "Joseph Chilliams"
        },
        {
            "id": "2223",
            "name": "Ravyn Lenae"
        }
    ]
}

artists = [
    Artist(artist_id="0002", name="Cam O'bi"),
    Artist(artist_id="0003", name="Raury"),
    Artist(artist_id="2222", name="Joseph Chilliams"),
    Artist(artist_id="2223", name="Ravyn Lenae")
]


class TestNetworkTopTracks:
    def test_get_top_tracks(self):
        network = Network(audio_features=["a", "b"], max_tracks=10, spotify=Mock())
        network.spotify.artist_top_tracks.return_value = tracks_response

        actual = network.get_top_tracks(Artist(artist_id="0001", name="Noname"))
        assert tracks == actual
        network.spotify.artist_top_tracks.assert_called_once_with("0001")

    def test_get_top_tracks_sad(self):
        network = Network(audio_features=["a", "b"], max_tracks=10, spotify=Mock())
        network.spotify.artist_top_tracks.side_effect = Exception("spotify machine broke")

        assert [] == network.get_top_tracks(Artist(artist_id="0001", name="Noname"))
        network.spotify.artist_top_tracks.assert_called_once_with("0001")

    def test_get_related_artists(self):
        network = Network(audio_features=["a", "b"], max_tracks=10, spotify=Mock())
        network.spotify.artist_related_artists.return_value = artists_response
        assert artists == network.get_related_artists(Artist(artist_id="0001", name="Noname"))
        network.spotify.artist_related_artists.assert_called_once_with("0001")

    def test_get_related_artists_sad(self):
        network = Network(audio_features=["a", "b"], max_tracks=10, spotify=Mock())
        network.spotify.artist_related_artists.side_effect = Exception("spotify machine broke")
        assert [] == network.get_related_artists(Artist(artist_id="0001", name="Noname"))
        network.spotify.artist_related_artists.assert_called_once_with("0001")

    def test_get_related_artists_none(self):
        network = Network(audio_features=["a", "b"], max_tracks=10, spotify=Mock())
        network.spotify.artist_related_artists.return_value = {"artists": []}
        assert [] == network.get_related_artists(Artist(artist_id="0001", name="Noname"))
        network.spotify.artist_related_artists.assert_called_once_with("0001")

    def test_put_audio_features(self):
        # setup
        tracks_with_audio_features_response = [
            {"id": "000", "poetic": 1.0, "excellence": 1.0},
            {"id": "111", "true": 1.0, "bop": 1.0},
            {"id": "222", "let's": 1.0, "gooo": 1.0}
        ]

        tracks_only = [track[0] for track in tracks]

        tracks_with_audio_features = copy.deepcopy(tracks_only)
        tracks_with_audio_features[0].with_attrs({"poetic": 1.0, "excellence": 1.0})
        tracks_with_audio_features[1].with_attrs({"bop": 1.0})

        network = Network(audio_features=["poetic", "excellence", "bop"], max_tracks=10, spotify=Mock())
        network.spotify.audio_features.return_value = tracks_with_audio_features_response

        # test
        network.put_audio_features(tracks_only)

        # check correctness
        assert tracks_with_audio_features == tracks_only
        network.spotify.audio_features.assert_called_once_with({"000": True, "111": True, "222": True}.keys())

    def test_put_audio_features_sad(self):
        # setup
        network = Network(audio_features=["poetic", "excellence", "bop"], max_tracks=10, spotify=Mock())
        network.spotify.audio_features.side_effect = Exception("spotify machine broke")

        tracks_only = [track[0] for track in tracks]
        expected = copy.deepcopy(tracks_only)

        # test
        network.put_audio_features(tracks_only)

        # check correctness
        assert expected == tracks_only
        network.spotify.audio_features.assert_called_once_with({"000": True, "111": True, "222": True}.keys())

    def test_put_audio_features_single(self):
        # setup
        network = Network(audio_features=["poetic", "excellence", "bop"], max_tracks=10, spotify=Mock())
        network.spotify.audio_features.return_value = []

        single_track = tracks[0][0]
        expected = copy.deepcopy(single_track)

        # test
        network.put_audio_features([single_track])

        # check correctness
        assert expected == single_track
        network.spotify.audio_features.assert_called_once_with({"000": True}.keys())
