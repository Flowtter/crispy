import os
import shutil

import pytest

from api.models.filter import Filter
from api.models.segment import Segment
from api.tools.enums import SupportedGames
from api.tools.video import extract_segments
from tests.constants import MAIN_VIDEO, MAIN_VIDEO_THEFINALS


@pytest.mark.parametrize(
    "frames_before, frames_after, offset, expected",
    [
        (0, 0, 0, [(3.375, 3.75), (4.25, 4.875)]),
        (8, 0, 0, [(2.375, 4.875)]),
        (0, 16, 0, [(3.375, 6.875)]),
        (0, 0, 8, [(3.375, 4.875)]),
        (500, 0, 0, [(0.0, 4.875)]),
    ],
    ids=[
        "simple",
        "frames_before",
        "frames_after",
        "offset",
        "frames_before_zero",
    ],
)
async def test_extract_segments(
    highlight, neural_network, frames_before, frames_after, offset, expected
):
    await highlight.extract_images_from_game(SupportedGames.VALORANT, 8)
    timestamps, _ = await extract_segments(
        highlight,
        neural_network,
        confidence=0.8,
        framerate=8,
        offset=offset,
        frames_before=frames_before,
        frames_after=frames_after,
    )
    assert timestamps == expected
    shutil.rmtree(highlight.images_path)


async def test_extract_segments_high_confidence(highlight, neural_network):
    await highlight.extract_images_from_game(SupportedGames.VALORANT, 8)
    timestamps, _ = await extract_segments(
        highlight,
        neural_network,
        confidence=0.99,
        framerate=8,
        offset=0,
        frames_before=0,
        frames_after=0,
    )
    assert timestamps == [(3.375, 3.75)]
    shutil.rmtree(highlight.images_path)


async def test_extract_segments_recompile_empty(highlight):
    highlight.local_filters = {}
    highlight.save()

    Segment(
        {
            "highlight_id": highlight.id,
            "path": MAIN_VIDEO,
            "start": 3.375,
            "end": 4.875,
            "enabled": True,
        }
    ).save()

    Filter(
        {"highlight_id": highlight.id, "filters": {"hflip": {"option": True}}}
    ).save()
    assert highlight.recompile()


@pytest.mark.parametrize(
    "filters",
    [
        {},
        {"blur": {"option": 51}},
        {"brightness": {"option": 7}},
        {"hflip": {"option": False}, "blur": {"option": 50}},
        {"hflip": {"option": False}, "blur": {"option": 51}},
    ],
    ids=[
        "remove_filter",
        "change_value",
        "new_filter",
        "add_new_filter",
        "add_new_filter_and_change_value",
    ],
)
async def test_extract_segments_recompile(highlight, filters):
    highlight.local_filters = {"blur": {"option": 50}}
    highlight.save()

    Segment(
        {
            "highlight_id": highlight.id,
            "path": MAIN_VIDEO,
            "start": 3.375,
            "end": 4.875,
            "enabled": True,
        }
    ).save()

    Filter({"highlight_id": highlight.id, "filters": filters}).save()
    assert highlight.recompile()


async def test_extract_segments_dont_recompile(highlight):
    highlight.local_filters = {"hflip": {"option": True}}
    highlight.save()

    Segment(
        {
            "highlight_id": highlight.id,
            "path": MAIN_VIDEO,
            "start": 3.375,
            "end": 4.875,
            "enabled": True,
        }
    ).save()

    Filter(
        {"highlight_id": highlight.id, "filters": {"hflip": {"option": True}}}
    ).save()
    assert not highlight.recompile()


@pytest.mark.parametrize(
    "old_filters, new_filters",
    [
        ([("brightness", 3)], [("brightness", 6)]),
        ([("vflip", True)], [("hflip", True)]),
        ([("vflip", True)], [("brightness", 4), ("vflip", True)]),
        ([("brightness", 4), ("vflip", True)], [("vflip", True)]),
    ],
    ids=["brightness_change", "vflip_hflip", "vflip_brightness", "brightness_vflip"],
)
async def test_extract_segment_recompile_filters(
    highlight, old_filters, new_filters, neural_network
):
    frames_before, frames_after, offset, expected = (0, 0, 8, [(3.375, 4.875)])
    _segment = Segment(
        {
            "highlight_id": highlight.id,
            "path": MAIN_VIDEO,
            "start": 3.375,
            "end": 4.875,
            "enabled": True,
            "filters": {},
        }
    ).save()
    for _filter, option in old_filters:
        _segment.filters[_filter] = option
    _segment.save()

    filt = Filter({"highlight_id": highlight.id, "filters": {}}).save()

    for _filter, option in new_filters:
        filt.filters[_filter] = option
    filt.save()

    await highlight.extract_images_from_game(SupportedGames.VALORANT, 8)
    timestamps, _ = await extract_segments(
        highlight,
        neural_network,
        confidence=0.8,
        framerate=8,
        offset=offset,
        frames_before=frames_before,
        frames_after=frames_after,
    )
    assert timestamps == expected
    shutil.rmtree(highlight.images_path)


@pytest.mark.parametrize(
    "old_filters, new_filters",
    [
        ([("brightness", 3)], [("brightness", 6)]),
        ([("vflip", True)], [("hflip", True)]),
    ],
    ids=[
        "brightness_change",
        "vflip_hflip",
    ],
)
async def test_extract_segment_recompile_global(
    highlight, old_filters, new_filters, neural_network
):
    frames_before, frames_after, offset, expected = (0, 0, 8, [(3.375, 4.875)])
    _segment = Segment(
        {
            "highlight_id": highlight.id,
            "path": MAIN_VIDEO,
            "start": 3.375,
            "end": 4.875,
            "enabled": True,
            "filters": {},
        }
    ).save()
    for _filter, option in old_filters:
        _segment.filters[_filter] = option
    _segment.save()

    filt = Filter({"global": True, "filters": {}}).save()

    for _filter, option in new_filters:
        filt.filters[_filter] = option
    filt.save()

    await highlight.extract_images_from_game(SupportedGames.VALORANT, 8)
    timestamps, _ = await extract_segments(
        highlight,
        neural_network,
        confidence=0.8,
        framerate=8,
        offset=offset,
        frames_before=frames_before,
        frames_after=frames_after,
    )
    assert timestamps == expected
    shutil.rmtree(highlight.images_path)


async def test_extract_segments_the_finals(highlight):
    highlight.path = MAIN_VIDEO_THEFINALS
    highlight.usernames = ["heximius", "sxr_raynox", "srx", "raynox"]
    highlight = highlight.save()

    await highlight.extract_images_from_game(SupportedGames.THEFINALS, 8)
    timestamps, _ = await extract_segments(
        highlight,
        None,
        confidence=0,
        framerate=8,
        offset=0,
        frames_before=0,
        frames_after=8,
        game=SupportedGames.THEFINALS,
    )
    assert timestamps == [
        (5.5, 6.75),
        (9.5, 10.75),
        (12.125, 13.5),
        (19.75, 21.75),
        (22.75, 28.0),
    ]
    shutil.rmtree(highlight.images_path)
    shutil.rmtree(os.path.join(os.path.dirname(highlight.images_path), "usernames"))
