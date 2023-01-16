import os
import shutil

from api.tools.ffmpeg import merge_videos
from tests.constants import MAIN_VIDEO


def test_merge_one_video(tmp_path):
    merge_path = os.path.join(tmp_path, "merged.mp4")
    main_video = os.path.join(tmp_path, "main-video.mp4")
    shutil.copy(MAIN_VIDEO, main_video)

    assert os.path.exists(main_video)
    assert not os.path.exists(merge_path)
    merge_videos([main_video], merge_path, False)
    assert os.path.exists(main_video)
    assert os.path.exists(merge_path)

    assert os.path.getsize(main_video) == os.path.getsize(merge_path)

    os.remove(merge_path)
    os.remove(main_video)
