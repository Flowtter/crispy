import os

from api.tools.audio import merge_musics
from tests.constants import MUSICS_PATH


def test_merge_musics(tmp_path):
    musics = sorted(os.listdir(MUSICS_PATH))

    merge_musics(
        [os.path.join(MUSICS_PATH, music) for music in musics],
        os.path.join(tmp_path, "merged.mp3"),
    )


def test_merge_musics_one(tmp_path):
    merge_musics(
        [os.path.join(MUSICS_PATH, "glass.mp3")],
        os.path.join(tmp_path, "merged.mp3"),
    )
