from graph.artist import Artist


class TestArtist:
    def test_equal(self):
        a = Artist(artist_id="123", name="the beatles")
        b = Artist(artist_id="123", name="the beatles")
        assert a == b

    def test_equal_with_diff_attr(self):
        a = Artist(artist_id="123", name="the beatles", attr={"brilliant": "yes"})
        b = Artist(artist_id="123", name="the beatles")
        assert a == b

    def test_not_equal(self):
        a = Artist(artist_id="123", name="the beatles")
        b = Artist(artist_id="456", name="the doors")
        assert a != b

    def test_not_equal_same_name(self):
        a = Artist(artist_id="123", name="Armageddon")
        b = Artist(artist_id="456", name="Armageddon")
        assert a != b

    def test_not_equal_same_id(self):
        a = Artist(artist_id="123", name="the beatles")
        b = Artist(artist_id="123", name="The Beatles")
        assert a != b
