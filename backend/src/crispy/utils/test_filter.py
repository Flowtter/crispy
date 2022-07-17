import os
from filter import filters
from ffmpeg_utils import apply_filter
from constants import TMP_PATH, CUT


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
    folders = os.listdir(TMP_PATH)
    folders = [f for f in folders if os.path.isdir(os.path.join(TMP_PATH, f))]
    for fold in folders:
        cut = os.listdir(os.path.join(TMP_PATH, fold, CUT))
        for i in range(len(cut)):
            cut[i] = os.path.join(TMP_PATH, fold, CUT, cut[i])
            apply_filter(cut[i], os.path.join(TMP_PATH, "test_brightness.mp4"))
