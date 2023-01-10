from enum import Enum
from typing import Tuple, Union
import moviepy.editor as mpe
from utils import moviepy_transi
from utils.constants import L


class NoValue(Enum):
    """
    Super class for filtes enum
    """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self.name}>"


class TransitionValue(NoValue):
    """
    Enum class containing all possible filters
    """

    SLIDE_IN = "slide_in"
    SLIDE_OUT = "slide_out"
    CROSSFADEIN = "crossfadein"
    CROSSFADEOUT = "crossfadeout"
    NONE = "none"


class Transition():
    """
    Class holding all transitions
    """

    def __init__(self, name: str, option: Union[Tuple[int, str],
                                                float]) -> None:
        if name in TransitionValue._value2member_map_:
            self.transi = TransitionValue._value2member_map_[name]
        else:
            L.error(f"{name} is not a valid transition")
            self.transi = TransitionValue.NONE
        self.option = option

    def __call__(self, video: mpe.VideoFileClip) -> None:
        if self.transi == TransitionValue.NONE:
            return video
        func = getattr(moviepy_transi, self.transi.value)
        return func(self.option, video)
