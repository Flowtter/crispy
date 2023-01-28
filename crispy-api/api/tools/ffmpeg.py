import os
import shutil
from typing import List, Optional

import moviepy.editor as mpe


async def merge_videos(
    videos_path: List[str],
    save_path: str,
    delete: bool = True,
    audio_path: Optional[str] = None,
) -> None:
    """
    Merge videos together

    :param videos_path: list of video paths
    :param save_path: path to save the merged video
    """
    videos_path = [video for video in videos_path if video is not None]

    if len(videos_path) <= 1 and audio_path is None:
        shutil.copy(videos_path[0], save_path)
    else:
        clips = []
        for filename in videos_path:
            clips.append(mpe.VideoFileClip(filename))

        final_clip = mpe.concatenate_videoclips(clips)

        if audio_path is not None and os.path.exists(audio_path):
            audios = [mpe.AudioFileClip(audio_path)]
            if final_clip.audio is not None:
                audios.append(final_clip.audio)

            final_audio = mpe.CompositeAudioClip(audios)
            final_audio = final_audio.subclip(0, final_clip.duration)
            final_clip.audio = final_audio

        final_clip = final_clip.subclip(
            t_end=(final_clip.duration - 1.0 / final_clip.fps)
        )
        final_clip.write_videofile(
            save_path, verbose=False, codec="libx264", logger=None
        )

        for clip in clips:
            clip.close()

    if delete:
        for filename in videos_path:
            if not filename or not os.path.exists(filename):
                continue
            os.remove(filename)
