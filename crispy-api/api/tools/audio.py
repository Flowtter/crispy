import os
import shutil
from typing import Any, List

import ffmpeg
from pydub import AudioSegment

from api.config import ASSETS


def merge_musics(audios: List[str], save_path: str) -> None:
    if len(audios) == 0:
        return
    if len(audios) == 1:
        shutil.copy(audios[0], save_path)
        return

    res = AudioSegment.from_file(audios.pop(0))
    for au in audios:
        res += AudioSegment.from_file(au)

    res.export(save_path)


def silence_if_no_audio(audio: Any, file: str) -> Any:
    p = ffmpeg.probe(file, select_streams="a")
    if not p["streams"]:
        return ffmpeg.input(os.path.join(ASSETS, "silence.mp3")).audio
    return audio
