import copy
import os
import shutil

import pytest

from api.models.highlight import Highlight
from api.models.segment import Segment
from api.tools.enums import SupportedGames
from tests.constants import MAIN_VIDEO_NO_AUDIO


async def test_highlight(highlight):
    assert highlight
    assert await Highlight.find_one(highlight.id)


async def test_extract_thumbnail(highlight):
    assert highlight.thumbnail_path is None
    assert await highlight.extract_thumbnail()
    assert highlight.thumbnail_path is not None
    assert os.path.exists(highlight.thumbnail_path)

    assert not await highlight.extract_thumbnail()
    assert highlight.thumbnail_path is not None
    assert os.path.exists(highlight.thumbnail_path)


async def test_extract_images(highlight):
    def post_process(image):
        image.putdata([(r, 0, b) for r, _, b in image.getdata()])
        return image

    assert highlight.images_path is None
    assert await highlight.extract_images(post_process, (0, 0, 64, 64), framerate=0.5)
    assert highlight.images_path is not None
    assert os.path.exists(highlight.images_path)

    assert not await highlight.extract_images(
        post_process, (0, 0, 64, 64), framerate=0.5
    )


@pytest.mark.parametrize(
    "highlight_path, timestamps",
    [
        (None, [(0, 1), (3, 5)]),
        (MAIN_VIDEO_NO_AUDIO, [(0, 1)]),
    ],
    ids=["with_audio", "no_audio"],
)
async def test_segment_video(highlight_path, timestamps, highlight):
    assert highlight.keyframes is not None

    if highlight_path is not None:
        highlight.path = highlight_path
        highlight = await highlight.save()

    assert highlight.segments_path is None
    result = await highlight.segment(timestamps)

    assert highlight.segments_path is not None
    assert os.path.exists(highlight.segments_path)

    segments = await Segment.find({"highlight_id": highlight.id}).to_list(None)
    assert len(segments) == len(timestamps)
    assert result == segments

    for segment, timestamp in zip(result, timestamps):
        assert segment.start == timestamp[0]
        assert segment.end == timestamp[1]
        assert segment.path == os.path.join(
            highlight.directory, "segments", f"{timestamp[0]}-{timestamp[1]}.mp4"
        )
        assert os.path.exists(segment.path)


async def test_segment_video_new_clips(highlight):
    assert highlight.segments_path is None

    results = []
    for segments in [[(0, 1), (3, 5)], [(0, 1), (3, 4)]]:
        results.append(await highlight.segment(segments))
        assert highlight.segments_path is not None
        assert os.path.exists(highlight.segments_path)
        for segment in results[-1]:
            assert os.path.exists(segment.path)

    assert not os.path.exists(os.path.join(highlight.directory, "segments", "3-5.mp4"))

    segments = await Segment.find({"highlight_id": highlight.id}).to_list(None)
    assert await Segment.find_one({"highlight_id": highlight.id, "end": 5}) is None

    assert len(segments) == 2
    assert results[-1] == segments
    for initial, new in zip(*results):
        if initial.start == new.start and initial.end == new.end:
            assert initial.id == new.id


async def test_segment_video_no_optimization(highlight):
    highlight.keyframes = [0, 2]

    await highlight.segment([(0.1, 1.5)])


async def test_segment_video_optimization(highlight):
    highlight.keyframes = [0, 1]

    await highlight.segment([(0.5012, 5)])


@pytest.mark.parametrize(
    "highlight_path, game",
    [
        (None, SupportedGames.VALORANT),
        (
            os.path.join("tests", "assets", "main-video-overwatch.mp4"),
            SupportedGames.OVERWATCH,
        ),
    ],
    ids=["valorant", "overwatch"],
)
async def test_extract_game_images(highlight, highlight_path, game):
    if highlight_path is not None:
        highlight.path = highlight_path
        highlight = await highlight.save()

    assert highlight.images_path is None
    assert await highlight.extract_images_from_game(game, framerate=1.5)
    assert highlight.images_path is not None
    assert os.path.exists(highlight.images_path)

    assert not await highlight.extract_images_from_game(game, framerate=1.5)


async def test_extract_game_images_not_supported(highlight):
    with pytest.raises(NotImplementedError):
        await highlight.extract_images_from_game("not_supported")


async def test_scale_video(highlight, tmp_path):
    tmp_video_path = os.path.join(tmp_path, "main-video.mp4")
    assert not os.path.exists(tmp_video_path)
    shutil.copy(highlight.path, tmp_video_path)
    highlight.path = tmp_video_path
    highlight = await highlight.save()
    await highlight.scale_video(480, 270, os.path.join(tmp_path, "backup"))
    assert os.path.exists(tmp_video_path)
    shutil.rmtree(os.path.join(tmp_path, "backup"))


async def test_scale_video_doesnt_exist(highlight):
    highlight.path = "doesnt_exist.mp4"
    await highlight.save()
    with pytest.raises(FileNotFoundError):
        await highlight.scale_video(480, 270)


async def test_remove(highlight):
    await highlight.segment([(0, 1)])
    assert await Segment.find_one({"highlight_id": highlight.id}) is not None

    await highlight.remove()
    assert not os.path.exists(highlight.directory)
    assert await Segment.find_one({"highlight_id": highlight.id}) is None
    assert await Highlight.find_one(highlight.id) is None


async def test_extract_keyframes(highlight):
    keyframes = copy.deepcopy(highlight.keyframes)

    highlight.keyframes = None
    await highlight.save()

    assert highlight.keyframes is None

    await highlight.extract_keyframes()
    assert highlight.keyframes is not None
    assert highlight.keyframes == keyframes
