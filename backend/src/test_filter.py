from utils.filter import filters
from pytube import YouTube


def test_class() -> None:
    crop = filters("   crop          ", "1")
    assert crop.filter.name == "CROP"
    crop = filters("   ZOOM          ", "1")
    assert crop.filter.name == "ZOOM"
    crop = filters("   CrOpdafd          ", "1")
    assert crop.filter.name == "NONE"
    crop = filters("   c rop          ", "1")
    assert crop.filter.name == "NONE"
    crop = filters("crop", "1")
    assert crop.filter.name == "CROP"
    crop = filters("   brightness                             \
    ", "1")
    assert crop.filter.name == "BRIGHTNESS"


def test_filter() -> None:
    """
    Load youtube video to test filters. Needs to call main.py manually to check
    """
    yt = YouTube(
        "https://www.youtube.com/watch?v=vWj6NxN7PsI&feature=youtu.be")
    yt.streams.order_by("resolution").desc().first().download(
        filename="backend/resources/video/0.mp4")
    print("Video downloaded")
