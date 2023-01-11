import os

import pytest

from api.models.highlight import Highlight


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
        (os.path.join("tests", "assets", "main-video-no-audio.mp4"), [(0, 1)]),
    ],
    ids=["with_audio", "no_audio"],
)
async def test_segment_video(highlight_path, timestamps, highlight):
    if highlight_path is not None:
        highlight.path = highlight_path
        highlight = await highlight.save()
        assert highlight.path == highlight_path

    assert highlight.segments_path is None
    result = await highlight.segment(timestamps)
    assert result == [
        os.path.join(
            highlight.directory, "segments", f"{timestamp[0]}-{timestamp[1]}.mp4"
        )
        for timestamp in timestamps
    ]
    assert highlight.segments_path is not None
    assert os.path.exists(highlight.segments_path)
