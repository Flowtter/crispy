import logging
from typing import Union

import ffmpeg

logger = logging.getLogger("uvicorn")


def blur(
    option: Union[str, bool, int, float], video: ffmpeg.nodes.FilterableStream
) -> ffmpeg.nodes.FilterableStream:
    """
    Increase or decrease the blur of the video based on the option
    """
    if type(option) == int or type(option) == float:
        video = video.filter("boxblur", option)
    else:
        logger.error(
            f"expected type({int} / {float}) got ({type(option)}) for filter ('blur')"
        )
    return video


def hflip(
    option: Union[str, bool, int, float], video: ffmpeg.nodes.FilterableStream
) -> ffmpeg.nodes.FilterableStream:
    """
    Flip horizontally the video
    """
    if type(option) == bool and option:
        video = video.hflip()
    else:
        logger.error(f"expected type({bool}) got ({type(option)}) for filter ('hflip')")
    return video


def vflip(
    option: Union[str, bool, int, float], video: ffmpeg.nodes.FilterableStream
) -> ffmpeg.nodes.FilterableStream:
    """
    Flip vertically the video
    """
    if type(option) == bool and option:
        video = video.vflip()
    else:
        logger.error(f"expected type({bool}) got ({type(option)}) for filter ('vflip')")
    return video


def brightness(
    option: Union[str, bool, int, float], video: ffmpeg.nodes.FilterableStream
) -> ffmpeg.nodes.FilterableStream:
    """
    Increase or decrease the brightness of the video based on the option
    """
    if type(option) == int or type(option) == float:
        video = video.hue(b=option)
    else:
        logger.error(
            f"expected type({int} / {float}) got ({type(option)}) for filter ('brightness')"
        )
    return video


def saturation(
    option: Union[str, bool, int, float], video: ffmpeg.nodes.FilterableStream
) -> ffmpeg.nodes.FilterableStream:
    """
    Increase or decrease the saturation of the video based on the option
    """
    if type(option) == int or type(option) == float:
        video = video.hue(s=option)
    else:
        logger.error(
            f"expected type({int} / {float}) got ({type(option)}) for filter ('saturation')"
        )
    return video


def zoom(
    option: Union[str, bool, int, float], video: ffmpeg.nodes.FilterableStream
) -> ffmpeg.nodes.FilterableStream:
    """
    Zoom the video based on the option
    """
    if (type(option) == int or type(option) == float) and option > 0:
        video = video.zoompan(
            z=option, fps=60, d=1, x="iw/2-(iw/zoom/2)", y="ih/2-(ih/zoom/2)"
        )
    else:
        logger.error(
            f"expected positive type({int} / {float}) got ({type(option)}) for filter ('zoom')"
        )
    return video


def grayscale(
    option: Union[str, bool, int, float], video: ffmpeg.nodes.FilterableStream
) -> ffmpeg.nodes.FilterableStream:
    """
    Turn the video into grayscale
    """
    if type(option) == bool and option:
        video = video.hue(s=0)
    else:
        logger.error(
            f"expected type({bool}) got ({type(option)}) for filter ('grayscale')"
        )
    return video
