from enum import Enum
import re
import ffmpeg


class no_value(Enum):
    """
    Super class for filtes enum
    """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self.name}>"


class filter_value(no_value):
    """
    Enum class containing all possible filters
    """

    CROP = 'crop'  # "crop"
    BLUR = 'Blur'  # "boxblur"
    SCALE = 'Scale'  # "scale"
    HFLIP = 'Hflip'  # "horizontal flip"
    VFLIP = 'Vflip'  # "vertical flip"
    BRIGHTNESS = 'Brightness'  # "b"
    SATURATION = 'Saturation'  # "s"
    ZOOM = 'Zoom'  # "zoom"
    GRAYSCALE = 'Grayscale'  # "hue=s=0"
    NONE = 'none'


def ex(video_path: str, save_path: str, filter_name: str,
       filter_option: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .filter(filter_name, filter_option)
        .output(save_path)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def crop(video_path: str, save_path: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .crop(x=960, y=540)
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def blur(video_path: str, save_path: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .filter("boxblur", "luma_radius=2:luma_power=1")
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def scale(video_path: str, save_path: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .filter('scale', 'w=1280:h=720')
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def hflip(video_path: str, save_path: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .hflip()
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def vflip(video_path: str, save_path: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .vflip()
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def brightness(video_path: str, save_path: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .hue(b=8)
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def saturation(video_path: str, save_path: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .hue(s=8)
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def zoom(video_path: str, save_path: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .zoom(zoom=8)
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def grayscale(video_path: str, save_path: str) -> None:
    (
        ffmpeg
        .input(video_path)
        .filter('format', "format=gray")
        # .filter('colorchannelmixer', '.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3')
        .output(save_path, start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


class filters():
    """
    Class holding all filters
    """

    def __init__(self, name: str) -> None:
        # Add other parameter for different filters later ?
        print(name)
        if re.search(r'^[\s]*crop[\s]*$', name, re.IGNORECASE):
            self.filter = filter_value.CROP
            self.f = {'f': crop}
        elif re.search(r'^[\s]*blur[\s]*$', name, re.IGNORECASE):
            self.filter = filter_value.BLUR
            self.f = {'f': blur}
        elif re.search(r'^[\s]*scale[\s]*$', name, re.IGNORECASE):
            self.filter = filter_value.SCALE
            self.f = {'f': scale}
        elif re.search(r'^[\s]*hflip[\s]*$', name, re.IGNORECASE):
            self.filter = filter_value.HFLIP
            self.f = {'f': hflip}
        elif re.search(r'^[\s]*vflip[\s]*$', name, re.IGNORECASE):
            self.filter = filter_value.VFLIP
            self.f = {'f': vflip}
        elif re.search(r'^[\s]*brightness[\s]*$', name, re.IGNORECASE):
            self.filter = filter_value.BRIGHTNESS
            self.f = {'f': brightness}
        elif re.search(r'^[\s]*saturation[\s]*$', name, re.IGNORECASE):
            self.filter = filter_value.SATURATION
            self.f = {'f': saturation}
        elif re.search(r'^[\s]*zoom[\s]*$', name, re.IGNORECASE):
            self.filter = filter_value.ZOOM
            self.f = {'f': zoom}
        elif re.search(r'^[\s]*grayscale[\s]*$', name, re.IGNORECASE):
            self.filter = filter_value.GRAYSCALE
            self.f = {'f': grayscale}
        else:
            self.filter = filter_value.NONE

    def execute(self, video_path: str, save_path: str) -> None:
        if self.filter == filter_value.NONE:
            return None
        return self.f['f'](video_path, save_path)
