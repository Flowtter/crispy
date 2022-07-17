import ffmpeg


def crop(video_path: str, save_path: str, _option: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .crop(x=960, y=540)
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def blur(video_path: str, save_path: str, option: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .filter("boxblur", option)  # "luma_radius=2:luma_power=1"
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def scale(video_path: str, save_path: str, option: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .filter("scale", option)  # "w=1280:h=720"
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def hflip(video_path: str, save_path: str, _option: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .hflip()
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def vflip(video_path: str, save_path: str, _option: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .vflip()
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def brightness(video_path: str, save_path: str, option: int) -> None:
    (
        ffmpeg
        .input(video_path)
        .hue(b=option)
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def saturation(video_path: str, save_path: str, option: int) -> None:
    (
        ffmpeg
        .input(video_path)
        .hue(s=option)
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def zoom(video_path: str, save_path: str, option: int) -> None:
    (
        ffmpeg
        .input(video_path)
        .zoompan(z=option, fps=60, d=1, x="iw/2-(iw/zoom/2)", y="ih/2-(ih/zoom/2)")
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def grayscale(video_path: str, save_path: str, _option: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .hue(s=0)
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable
