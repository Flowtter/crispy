import shutil

import pytest

from api.tools.enums import SupportedGames
from api.tools.video import extract_segments


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
    highlight.save()
    timestamps, _ = await extract_segments(
        highlight,
        neural_network,
        confidence=0.8,
        framerate=8,
        offset=offset,
        frames_before=frames_before,
        frames_after=frames_after,
    )
    shutil.rmtree(highlight.images_path)
    assert timestamps == expected


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
    shutil.rmtree(highlight.images_path)
    assert timestamps == [(3.375, 3.75)]
