from enum import Enum
from utils import ffmpeg_filters
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

    CROP = "crop"  # "crop"
    BLUR = "blur"  # "boxblur"
    SCALE = "scale"  # "scale"
    HFLIP = "hflip"  # "horizontal flip"
    VFLIP = "vflip"  # "vertical flip"
    BRIGHTNESS = "brightness"  # "b"
    SATURATION = "saturation"  # "s"
    ZOOM = "zoom"  # "zoom"
    GRAYSCALE = "grayscale"  # "hue=s=0"
    NONE = "none"


class filters():
    """
    Class holding all filters
    """

    def __init__(self, name: str, option: str) -> None:
        if name in filter_value._value2member_map_:
            self.filter = filter_value._value2member_map_[name]
        else:
            self.filter = filter_value.NONE
        self.option = option

    def __call__(self, video: ffmpeg.nodes.FilterableStream) -> None:
        if self.filter == filter_value.NONE:
            return video
        func = getattr(ffmpeg_filters, self.filter.value)
        return func(self.option, video)
