from typing import Union
from utils.constants import L
import ffmpeg


def crop(
        option: Union[str, bool, int, float],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    """
    Crop a video in 960 x 540 pixels
    """
    if type(option) == bool and option:
        video = video.crop(960, 540)
    else:
        L.error(
            f"expected type({bool}) got ({type(option)}) for filter ('crop')")
    return video


def blur(
        option: Union[str, bool, int, float],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    """
    Increase or decrease the blur of the video based on the option
    """
    if type(option) == int or type(option) == float:
        video = video.filter("boxblur", option)
    else:
        L.error(
            f"expected type({int} / {float}) got ({type(option)}) for filter ('blur')"
        )
    return video


def scale(
        option: Union[str, bool, int, float],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    """
    Scale a video based on the option (e.g 'w=1920:h=1280')
    """
    if type(option) == str:
        video = video.filter("scale", option)
    else:
        L.error(
            f"expected type({str}) got ({type(option)}) for filter ('scale')")
    return video


def hflip(
        option: Union[str, bool, int, float],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    """
    Flip horizontally the video
    """
    if type(option) == bool and option:
        video = video.hflip()
    else:
        L.error(
            f"expected type({bool}) got ({type(option)}) for filter ('hflip')")
    return video


def vflip(
        option: Union[str, bool, int, float],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    """
    Flip vertically the video
    """
    if type(option) == bool and option:
        video = video.vflip()
    else:
        L.error(
            f"expected type({bool}) got ({type(option)}) for filter ('vflip')")
    return video


def brightness(
        option: Union[str, bool, int, float],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    """
    Increase or decrease the brightness of the video based on the option
    """
    if type(option) == int or type(option) == float:
        video = video.hue(b=option)
    else:
        L.error(
            f"expected type({int} / {float}) got ({type(option)}) for filter ('brightness')"
        )
    return video


def saturation(
        option: Union[str, bool, int, float],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    """
    Increase or decrease the saturation of the video based on the option
    """
    if type(option) == int or type(option) == float:
        video = video.hue(s=option)
    else:
        L.error(
            f"expected type({int} / {float}) got ({type(option)}) for filter ('saturation')"
        )
    return video


def zoom(
        option: Union[str, bool, int, float],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    """
    Zoom the video based on the option (can only be positive)
    """
    if type(option) == int or type(option) == float:
        video = video.zoompan(z=option,
                              fps=60,
                              d=1,
                              x="iw/2-(iw/zoom/2)",
                              y="ih/2-(ih/zoom/2)")
    else:
        L.error(
            f"expected type({int} / {float}) got ({type(option)}) for filter ('zoom')"
        )
    return video


def grayscale(
        option: Union[str, bool, int, float],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    """
    Turn the video into grayscale
    """
    if type(option) == bool and option:
        video = video.hue(s=0)
    else:
        L.error(
            f"expected type({bool}) got ({type(option)}) for filter ('grayscale')"
        )
    return video
