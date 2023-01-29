import os
import shutil
import subprocess

import pytest

from api.tools.ffmpeg import merge_videos
from tests.constants import MAIN_MUSIC, MAIN_VIDEO, MAIN_VIDEO_NO_AUDIO


async def test_merge_one_video(tmp_path):
    merge_path = os.path.join(tmp_path, "merged.mp4")
    main_video = os.path.join(tmp_path, "main-video.mp4")
    shutil.copy(MAIN_VIDEO, main_video)

    assert os.path.exists(main_video)
    assert not os.path.exists(merge_path)
    await merge_videos([main_video], merge_path, False)
    assert os.path.exists(main_video)
    assert os.path.exists(merge_path)

    assert os.path.getsize(main_video) == os.path.getsize(merge_path)

    os.remove(merge_path)
    os.remove(main_video)


async def test_merge_two_videos(tmp_path):
    merge_path = os.path.join(tmp_path, "merged.mp4")
    main_video = os.path.join(tmp_path, "main-video.mp4")
    shutil.copy(MAIN_VIDEO, main_video)

    main_video2 = os.path.join(tmp_path, "main-video2.mp4")
    shutil.copy(MAIN_VIDEO, main_video2)

    assert os.path.exists(main_video)
    assert os.path.exists(main_video2)
    assert not os.path.exists(merge_path)
    await merge_videos([main_video, main_video2, None], merge_path, False)
    assert os.path.exists(main_video)
    assert os.path.exists(main_video2)
    assert os.path.exists(merge_path)

    os.remove(main_video)
    os.remove(main_video2)


async def test_merge_two_videos_delete(tmp_path):
    merge_path = os.path.join(tmp_path, "merged.mp4")

    main_video = os.path.join(tmp_path, "main-video.mp4")
    shutil.copy(MAIN_VIDEO, main_video)

    main_video2 = os.path.join(tmp_path, "main-video2.mp4")
    shutil.copy(MAIN_VIDEO, main_video2)

    assert os.path.exists(main_video)
    assert os.path.exists(main_video2)
    assert not os.path.exists(merge_path)
    await merge_videos([main_video, main_video2, main_video, None], merge_path, True)
    assert not os.path.exists(main_video)
    assert not os.path.exists(main_video2)
    assert os.path.exists(merge_path)

    os.remove(merge_path)


@pytest.mark.parametrize(
    "video",
    [
        (MAIN_VIDEO),
        (MAIN_VIDEO_NO_AUDIO),
    ],
)
async def test_merge_video_with_music(tmp_path, video):
    merge_path = os.path.join(tmp_path, "merged.mp4")
    main_video = os.path.join(tmp_path, "main-video.mp4")
    shutil.copy(video, main_video)

    main_music = os.path.join(tmp_path, "main-music.mp3")
    shutil.copy(MAIN_MUSIC, main_music)

    assert os.path.exists(main_video)
    assert os.path.exists(main_music)
    assert not os.path.exists(merge_path)
    await merge_videos([main_video], merge_path, False, main_music)
    assert os.path.exists(main_video)
    assert os.path.exists(main_music)
    assert os.path.exists(merge_path)

    ffprobe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=index",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            merge_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert ffprobe.stdout == "0\n1\n"
    os.remove(main_video)
    os.remove(main_music)
    os.remove(merge_path)
