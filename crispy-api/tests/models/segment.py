import os
import shutil

from tests.constants import MAIN_VIDEO


async def test_segment_name(segment):
    assert segment.name == f"{segment.start}-{segment.end}"


async def test_copy_video_in_lower_resolution(segment, tmp_path):
    segment.path = os.path.join(tmp_path, "test.mp4")
    shutil.copy(MAIN_VIDEO, segment.path)

    assert segment.downscaled_path is None
    assert await segment.copy_video_in_lower_resolution() is True

    assert segment.downscaled_path is not None
    assert os.path.exists(segment.downscaled_path)

    assert await segment.copy_video_in_lower_resolution() is False
