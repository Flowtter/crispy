import os
import shutil
import subprocess
from typing import List


def merge_videos(videos_path: List[str], save_path: str, delete: bool = True) -> None:
    """
    Merge videos together

    :param videos_path: list of video paths
    :param save_path: path to save the merged video
    """
    if len(videos_path) <= 1:
        shutil.copy(videos_path[0], save_path)
        return

    save_path_no_ext = os.path.splitext(save_path)[0]
    list_path = f"{save_path_no_ext}_merge_list.txt"
    with open(list_path, "w") as f:
        for video_path in videos_path:
            f.write(f"file '{video_path}'\n")

    subprocess.run(
        [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_path,
            "-c",
            "copy",
            "-y",
            "-loglevel",
            "error",
            save_path,
        ]
    )

    os.remove(list_path)
    if delete:
        for filename in videos_path:
            os.remove(filename)
