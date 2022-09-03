from typing import Tuple
import moviepy.editor as mpe


def slide_in(option: Tuple[int, str],
             video: mpe.VideoFileClip) -> mpe.VideoFileClip:
    """
    Apply a slide in transition to the current clip
    """
    video = video.fx(mpe.transfx.slide_in, option[0], option[1])
    return video


def slide_out(option: Tuple[int, str],
              video: mpe.VideoFileClip) -> mpe.VideoFileClip:
    """
    Apply a slide out transition to the current clip
    """
    video = video.fx(mpe.transfx.slide_out, option[0], option[1])
    return video


def crossfadein(option: float, video: mpe.VideoFileClip) -> mpe.VideoFileClip:
    """
    Apply a cross fade in effect to the current clip
    """
    video = video.crossfadein(option)
    return video


def crossfadeout(option: float, video: mpe.VideoFileClip) -> mpe.VideoFileClip:
    """
    Apply a cross fade out in effect to the current clip
    """
    video = video.crossfadeout(option)
    return video


def fadeout(option: float, video: mpe.VideoFileClip) -> mpe.VideoFileClip:
    """
    Apply a fadeout effect to the current clip
    """
    video = video.fadeout(option)
    return video
