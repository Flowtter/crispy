from typing import Union
import ffmpeg


def crop(
        option: Union[str, bool, int],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.cop(960, 540) if type(option) == bool and option else video
    return video


def blur(
        option: Union[str, bool, int],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.filter("boxblur", option) if type(option) == int else video
    return video


def scale(
        option: Union[str, bool, int],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.filter("scale", option) if type(option) == str else video
    return video


def hflip(
        option: Union[str, bool, int],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.hflip() if type(option) == bool and option else video
    return video


def vflip(
        option: Union[str, bool, int],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.vflip() if type(option) == bool and option else video
    return video


def brightness(
        option: Union[str, bool, int],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.hue(b=option) if type(option) == int else video
    return video


def saturation(
        option: Union[str, bool, int],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.hue(s=option) if type(option) == int else video
    return video


def zoom(
        option: Union[str, bool, int],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.zoompan(
        z=option, fps=60, d=1, x="iw/2-(iw/zoom/2)",
        y="ih/2-(ih/zoom/2)") if type(option) == int else video
    return video


def grayscale(
        option: Union[str, bool, int],
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.hue(s=0) if type(option) == bool and option else video
    return video
