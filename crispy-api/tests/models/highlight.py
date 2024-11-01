import os
import shutil
import time

import pytest

from api.models.highlight import Highlight
from api.models.segment import Segment
from api.tools.enums import SupportedGames
from tests.constants import (
    MAIN_VIDEO_CSGO2,
    MAIN_VIDEO_LEAGUE,
    MAIN_VIDEO_NO_AUDIO,
    MAIN_VIDEO_OVERWATCH,
    MAIN_VIDEO_THE_FINALS,
)


async def test_highlight(highlight):
    assert highlight
    assert Highlight.find_one(highlight.id)


async def test_highlight_name(highlight):
    assert highlight.name == "main-video"


async def test_extract_thumbnails(highlight):
    assert highlight.thumbnail_path is None
    await highlight.extract_thumbnails()
    assert highlight.thumbnail_path is not None
    assert os.path.exists(highlight.thumbnail_path)
    assert os.path.exists(highlight.thumbnail_path_full_size)
    assert highlight.thumbnail_path_full_size != highlight.thumbnail_path

    shutil.rmtree(highlight.directory)


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
    if highlight_path is not None:
        highlight.path = highlight_path
        highlight = highlight.save()

    assert highlight.segments_path is None
    result = await highlight.extract_segments(timestamps)

    assert highlight.segments_path is not None
    assert os.path.exists(highlight.segments_path)

    segments = Segment.find({"highlight_id": highlight.id}).to_list(None)
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
        results.append(await highlight.extract_segments(segments))
        assert highlight.segments_path is not None
        assert os.path.exists(highlight.segments_path)
        for segment in results[-1]:
            assert os.path.exists(segment.path)

    assert not os.path.exists(os.path.join(highlight.directory, "segments", "3-5.mp4"))

    segments = Segment.find({"highlight_id": highlight.id}).to_list(None)
    assert Segment.find_one({"highlight_id": highlight.id, "end": 5}) is None

    assert len(segments) == 2
    assert results[-1] == segments
    for initial, new in zip(*results):
        if initial.start == new.start and initial.end == new.end:
            assert initial.id == new.id


async def test_segment_video_segments_are_removed(highlight, tmp_path):
    initial_time = time.time()
    await highlight.extract_segments([(0, 1)])
    duration = time.time() - initial_time
    assert highlight.segments_path is not None
    assert os.path.exists(highlight.segments_path)

    segment = Segment.find_one({"highlight_id": highlight.id})
    assert segment

    assert segment.path is not None
    assert os.path.exists(segment.path)

    current_time = time.time()
    await highlight.extract_segments([(0, 1)])
    assert time.time() - current_time < duration
    assert highlight.segments_path is not None
    assert os.path.exists(highlight.segments_path)

    segment = Segment.find_one({"highlight_id": highlight.id})
    assert segment

    assert segment.path is not None
    assert os.path.exists(segment.path)

    downscaled_path = os.path.join(tmp_path, "downscaled.mp4")
    shutil.copy(segment.path, downscaled_path)

    segment.downscaled_path = downscaled_path
    segment.save()

    assert os.path.exists(segment.downscaled_path)
    await highlight.extract_segments([])
    assert highlight.segments_path is not None

    assert not os.path.exists(segment.downscaled_path)
    assert not os.path.exists(segment.path)

    assert not Segment.find_one({"highlight_id": highlight.id})

    assert os.listdir(highlight.directory) == ["segments"]
    assert os.listdir(highlight.segments_path) == []

    os.rmdir(highlight.segments_path)


@pytest.mark.parametrize(
    "highlight_path, game, rate",
    [
        (None, SupportedGames.VALORANT, 8),
        (MAIN_VIDEO_OVERWATCH, SupportedGames.OVERWATCH, 1.5),
        (MAIN_VIDEO_CSGO2, SupportedGames.CSGO2, 1.5),
        (MAIN_VIDEO_THE_FINALS, SupportedGames.THE_FINALS, 0.75),
        (MAIN_VIDEO_LEAGUE, SupportedGames.LEAGUE_OF_LEGENDS, 1.5),
    ],
    ids=["valorant", "overwatch", "csgo2", "the-finals", "league-of-legends"],
)
async def test_extract_game_images(highlight, highlight_path, game, rate):
    if highlight_path is not None:
        highlight.path = highlight_path
        highlight = highlight.save()

    assert highlight.images_path is None
    assert await highlight.extract_images_from_game(game, framerate=rate)
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
    highlight = highlight.save()
    await highlight.scale_video(480, 270, os.path.join(tmp_path, "backup"))
    assert os.path.exists(tmp_video_path)
    shutil.rmtree(os.path.join(tmp_path, "backup"))


async def test_scale_video_doesnt_exist(highlight):
    highlight.path = "doesnt_exist.mp4"
    highlight.save()
    with pytest.raises(FileNotFoundError):
        await highlight.scale_video(480, 270)


async def test_remove(highlight):
    await highlight.extract_segments([(0, 1)])
    assert Segment.find_one({"highlight_id": highlight.id}) is not None

    await highlight.remove()
    assert not os.path.exists(highlight.directory)
    assert Segment.find_one({"highlight_id": highlight.id}) is None
    assert Highlight.find_one(highlight.id) is None


async def test_extract_snippet_in_lower_resolution(highlight):
    assert highlight.snippet_path is None
    assert await highlight.extract_snippet_in_lower_resolution()
    assert highlight.snippet_path is not None
    assert os.path.exists(highlight.snippet_path)
    assert not await highlight.extract_snippet_in_lower_resolution()


# WARNING: This test depends on the segment function working properly
async def test_concat_segments(highlight):
    assert not await highlight.concatenate_segments()

    await highlight.extract_segments([(0, 1), (3, 5)])
    assert os.path.exists(highlight.segments_path)

    assert await highlight.concatenate_segments()
    assert Highlight.find_one(highlight.id).merge_path is not None
    assert os.path.exists(highlight.path)
