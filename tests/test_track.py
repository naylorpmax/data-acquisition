from acquisition.track import Track


class TestTrack:
    def test_equal(self):
        a = Track(track_id="123", name="Trust Nobody", album="Cheap Queen", album_type="album")
        b = Track(track_id="123", name="Trust Nobody", album="Cheap Queen", album_type="album")

        assert a == b

    def test_equal_with_attr(self):
        a = Track(track_id="123", name="Trust Nobody", album="Cheap Queen", album_type="album", attr={"fire": True})
        b = Track(track_id="123", name="Trust Nobody", album="Cheap Queen", album_type="album")

        assert a == b

    def test_not_equal_album(self):
        a = Track(track_id="123", name="Trust Nobody", album="Cheap Queen", album_type="album")
        b = Track(track_id="123", name="Trust Nobody", album="Cheap Queen (Deluxe)", album_type="album")

        assert a != b

    def test_not_equal_album_type(self):
        a = Track(track_id="123", name="Trust Nobody", album="Cheap Queen", album_type="album")
        b = Track(track_id="123", name="Trust Nobody", album="Cheap Queen", album_type="single")

        assert a != b

    def test_not_equal_name(self):
        a = Track(track_id="123", name="Trust Nobody", album="Cheap Queen", album_type="album")
        b = Track(track_id="123", name="Hit the Back", album="Cheap Queen", album_type="album")

        assert a != b

    def test_not_equal_id(self):
        a = Track(track_id="123", name="Trust Nobody", album="Cheap Queen", album_type="album")
        b = Track(track_id="456", name="Trust Nobody", album="Cheap Queen", album_type="album")

        assert a != b

    def test_set_attr(self):
        attr = {"fire": True}
        a = Track(track_id="123", name="Trust Nobody", album="Cheap Queen", album_type="album")
        a.with_attrs(attr)

        assert a.attr == attr
