import os
from typing import Any

import ffmpeg

from api.config import ASSETS


def silence_if_no_audio(audio: Any, file: str) -> Any:
    p = ffmpeg.probe(file, select_streams="a")
    if not p["streams"]:
        return ffmpeg.input(os.path.join(ASSETS, "silence.mp3")).audio
    return audio
