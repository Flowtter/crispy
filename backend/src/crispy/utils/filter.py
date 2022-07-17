from enum import Enum
import re
import ffmpeg_filters


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

    CROP = "crop"  # "crop"
    BLUR = "Blur"  # "boxblur"
    SCALE = "Scale"  # "scale"
    HFLIP = "Hflip"  # "horizontal flip"
    VFLIP = "Vflip"  # "vertical flip"
    BRIGHTNESS = "Brightness"  # "b"
    SATURATION = "Saturation"  # "s"
    ZOOM = "Zoom"  # "zoom"
    GRAYSCALE = "Grayscale"  # "hue=s=0"
    NONE = "none"


class filters():
    """
    Class holding all filters
    """

    def __init__(self, name: str, option: str) -> None:
        # Add other parameter for different filters later ?
        self.option = option
        if re.search(r"^[\s]*crop[\s]*$", name, re.IGNORECASE):
            self.filter = filter_value.CROP
            self.f = "crop"
        elif re.search(r"^[\s]*blur[\s]*$", name, re.IGNORECASE):
            self.filter = filter_value.BLUR
            self.f = "blur"
        elif re.search(r"^[\s]*scale[\s]*$", name, re.IGNORECASE):
            self.filter = filter_value.SCALE
            self.f = "scale"
        elif re.search(r"^[\s]*hflip[\s]*$", name, re.IGNORECASE):
            self.filter = filter_value.HFLIP
            self.f = "hflip"
        elif re.search(r"^[\s]*vflip[\s]*$", name, re.IGNORECASE):
            self.filter = filter_value.VFLIP
            self.f = "vflip"
        elif re.search(r"^[\s]*brightness[\s]*$", name, re.IGNORECASE):
            self.filter = filter_value.BRIGHTNESS
            self.f = "brightness"
        elif re.search(r"^[\s]*saturation[\s]*$", name, re.IGNORECASE):
            self.filter = filter_value.SATURATION
            self.f = "saturation"
        elif re.search(r"^[\s]*zoom[\s]*$", name, re.IGNORECASE):
            self.filter = filter_value.ZOOM
            self.f = "zoom"
        elif re.search(r"^[\s]*grayscale[\s]*$", name, re.IGNORECASE):
            self.filter = filter_value.GRAYSCALE
            self.f = "grayscale"
        else:
            self.filter = filter_value.NONE

    def __call__(self, video_path: str, save_path: str) -> None:
        if self.filter == filter_value.NONE:
            return None
        func = getattr(ffmpeg_filters, self.f)
        return func(video_path, save_path, self.option)
