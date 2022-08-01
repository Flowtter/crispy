import os
from typing import List

from pydub import AudioSegment

from utils.constants import MUSIC_MERGE_FOLDER, TMP_PATH


def concat_musics(audios: List[str]) -> None:
    save_path = os.path.join(MUSIC_MERGE_FOLDER, "merged.mp3")
    json = os.path.join(TMP_PATH, "music.json")

    if os.path.exists(save_path) and not os.path.exists(json):
        return

    if os.path.exists(json):
        os.remove(json)

    print("Recompiling music")

    if not os.path.exists(MUSIC_MERGE_FOLDER):
        os.mkdir(MUSIC_MERGE_FOLDER)
    res = AudioSegment.from_mp3(audios.pop(0))
    for au in audios:
        res += AudioSegment.from_mp3(au)

    res.export(save_path)
