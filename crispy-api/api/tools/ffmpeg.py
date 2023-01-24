import os
import shutil
from typing import List

import moviepy.editor as mpe


async def merge_videos(
    videos_path: List[str], save_path: str, delete: bool = True
) -> None:
    """
    Merge videos together

    :param videos_path: list of video paths
    :param save_path: path to save the merged video
    """
    videos_path = [video for video in videos_path if video is not None]

    if len(videos_path) <= 1:
        shutil.copy(videos_path[0], save_path)
    else:
        clips = []
        for filename in videos_path:
            clips.append(mpe.VideoFileClip(filename))
        print(clips)
        final_clip = mpe.concatenate_videoclips(clips)

        final_clip = final_clip.subclip(
            t_end=(final_clip.duration - 1.0 / final_clip.fps)
        )
        final_clip.write_videofile(save_path, verbose=False, codec="libx264")

        for clip in clips:
            clip.close()

    if delete:
        for filename in videos_path:
            if not filename or not os.path.exists(filename):
                continue
            os.remove(filename)
