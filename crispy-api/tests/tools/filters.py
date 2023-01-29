import os.path

import ffmpeg
import pytest

from api.models.filter import Filter
from tests.constants import MAIN_SEGMENT


@pytest.mark.parametrize(
    "_filter, option",
    [
        ("blur", 50),
        ("brightness", 6),
        ("grayscale", True),
        ("hflip", True),
        ("saturation", 6),
        ("vflip", True),
        ("zoom", 2),
        ("blur", True),
        ("brightness", True),
        ("grayscale", 2),
        ("hflip", 2),
        ("saturation", True),
        ("vflip", 2),
        ("zoom", True),
        ("wrong", True),
    ],
    ids=[
        "blur",
        "brightness",
        "grayscale",
        "hflip",
        "saturation",
        "vflip",
        "zoom",
        "blur_nok",
        "brightness_nok",
        "grayscale_nok",
        "hflip_nok",
        "saturation_nok",
        "vflip_nok",
        "zoom_nok",
        "wrong",
    ],
)
async def test_apply_filter(_filter, option, highlight, tmp_path):
    Filter({"highlight_id": highlight.id, "filters": {_filter: option}}).save()

    out_path = os.path.join(tmp_path, f"{_filter}.mp4")
    ffmpeg.input(MAIN_SEGMENT).apply_filters(highlight.id).output(
        out_path
    ).overwrite_output().run(quiet=True)
    highlight.path = os.path.join(tmp_path, f"{_filter}.mp4")


@pytest.mark.parametrize(
    "vflip",
    [
        (True),
        (False),
    ],
    ids=[
        "vflip",
        "vflip_nok",
    ],
)
@pytest.mark.parametrize(
    "hflip",
    [
        (True),
        (False),
    ],
    ids=[
        "hflip",
        "hflip_nok",
    ],
)
async def test_apply_many_filters(highlight, vflip, hflip, tmp_path):
    _filter = Filter({"highlight_id": highlight.id, "filters": {}}).save()
    assert Filter.find_one({"global": True}) is None

    _filter.filters["vflip"] = vflip
    _filter.filters["hflip"] = hflip

    _filter.save()

    out_path = os.path.join(tmp_path, "vflip_hflip.mp4")
    ffmpeg.input(MAIN_SEGMENT).apply_filters(highlight.id).output(
        out_path
    ).overwrite_output().run(quiet=True)
    highlight.path = os.path.join(tmp_path, "vflip_hflip.mp4")
