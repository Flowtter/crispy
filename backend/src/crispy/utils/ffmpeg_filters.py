import ffmpeg


def crop(
        _option: str,
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.crop(x=960, y=540)
    return video


def blur(
        option: str,
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.filter("boxblur", option)  # "luma_radius=2:luma_power=1"
    return video


def scale(
        option: str,
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.filter("scale", option)  # "w=1280:h=720"
    return video


def hflip(
        _option: str,
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.hflip()
    return video


def vflip(
        _option: str,
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.vflip()
    return video


def brightness(
        option: int,
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.hue(b=option)
    return video


def saturation(
        option: int,
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.hue(s=option)
    return video


def zoom(
        option: int,
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.zoompan(z=option,
                          fps=60,
                          d=1,
                          x="iw/2-(iw/zoom/2)",
                          y="ih/2-(ih/zoom/2)")
    return video


def grayscale(
        _option: str,
        video: ffmpeg.nodes.FilterableStream) -> ffmpeg.nodes.FilterableStream:
    video = video.hue(s=0)
    return video
