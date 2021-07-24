from graph.playlist import Playlist
from graph.track import Track
from graph.artist import Artist


playlist = Playlist(playlist_id="123", name="sleep with a baseball bat", entries=[
    (
        Track(track_id="000", name="Sleep with a Baseball Bat", album="Good Grief", album_type="album"),
        [Artist(artist_id="0001", name="Cosmic Johnny")]
    ),
    (
        Track(track_id="111", name="Riot for Descendant Command", album="Oversleepers International",
              album_type="album"),
        [Artist(artist_id="1111", name="Emperor X")]
    ),
    (
        Track(track_id="222", name="Forever", album="Telefone", album_type="album"),
        [
            Artist(artist_id="2221", name="Noname"),
            Artist(artist_id="2222", name="Joseph Chilliams"),
            Artist(artist_id="2223", name="Ravyn Lenae")
        ]
    )
])


class TestPlaylist:
    def test_get_artists(self):
        artists = playlist.get_artists()

        assert sorted([
            Artist(artist_id="0001", name="Cosmic Johnny"),
            Artist(artist_id="1111", name="Emperor X"),
            Artist(artist_id="2221", name="Noname"),
            Artist(artist_id="2222", name="Joseph Chilliams"),
            Artist(artist_id="2223", name="Ravyn Lenae")
        ], key=lambda a: a.id) == sorted(artists, key=lambda a: a.id)
