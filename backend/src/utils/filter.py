from enum import Enum
from typing import Union

import ffmpeg
from utils import ffmpeg_filters
from utils.constants import L


class NoValue(Enum):
    """
    Super class for filtes enum
    """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self.name}>"


class FilterValue(NoValue):
    """
    Enum class containing all possible filters
    """

    BLUR = "blur"  # "boxblur"
    SCALE = "scale"  # "scale"
    HFLIP = "hflip"  # "horizontal flip"
    VFLIP = "vflip"  # "vertical flip"
    BRIGHTNESS = "brightness"  # "b"
    SATURATION = "saturation"  # "s"
    ZOOM = "zoom"  # "zoom"
    GRAYSCALE = "grayscale"  # "hue=s=0"
    NONE = "none"


class Filters:
    """
    Class holding all filters
    """

    def __init__(self, name: str, option: Union[str, bool, int]) -> None:
        if name in FilterValue._value2member_map_:
            self.filter = FilterValue._value2member_map_[name]
        else:
            L.error(f"{name} is not a valid filter")
            self.filter = FilterValue.NONE
        self.option = option

    def __call__(self, video: ffmpeg.nodes.FilterableStream) -> None:
        if self.filter == FilterValue.NONE:
            return video
        func = getattr(ffmpeg_filters, self.filter.value)
        return func(self.option, video)
