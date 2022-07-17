from filter import filters


def test_class() -> None:
    crop = filters("   crop          ")
    assert crop.filter.name == "CROP"
    crop = filters("   ZOOM          ")
    assert crop.filter.name == "ZOOM"
    crop = filters("   CrOpdafd          ")
    assert crop.filter.name == "NONE"
    crop = filters("   c rop          ")
    assert crop.filter.name == "NONE"
    crop = filters("crop")
    assert crop.filter.name == "CROP"
    crop = filters("   brightness                             \
    ")
    assert crop.filter.name == "BRIGHTNESS"
