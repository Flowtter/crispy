import logging
from enum import Enum
from typing import Any, Callable, Dict, Union

import ffmpeg
from ffmpeg.nodes import filter_operator

from api.models.filter import Filter
from api.tools import ffmpeg_filters
from api.tools.utils import sanitize_dict

logger = logging.getLogger("uvicorn")


class FilterValue(str, Enum):
    """
    Enum class containing all possible filters
    """

    BLUR = "blur"  # "boxblur"
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
            logger.error(f"{name} is not a valid filter")
            self.filter = FilterValue.NONE
        self.option = option

    def __call__(
        self, video: ffmpeg.nodes.FilterableStream
    ) -> Union[ffmpeg.nodes.FilterableStream, Callable]:
        if self.filter == FilterValue.NONE:
            return video
        callable = getattr(ffmpeg_filters, self.filter.value)
        return callable(self.option, video)


@filter_operator()
def apply_filters(streams: Any, highlight_id: str) -> Any:
    """
    Apply specific filters for each video

    :param streams: current stream
    :param highlight_id: highlight id
    """
    global_filters: Dict[str, Any] = {}

    global_filters = {}
    if _global_filters := Filter.find_one({"global": True}):
        global_filters = sanitize_dict(_global_filters.filters or {})

    highlight_filters: Dict[str, Any] = {}
    if _highlight_filters := Filter.find_one({"highlight_id": highlight_id}):
        highlight_filters = sanitize_dict(_highlight_filters.filters or {})

    filters = {**global_filters, **highlight_filters}

    for _filter in filters:
        video_filter = Filters(_filter, filters[_filter])
        streams = video_filter(streams)
    return streams
