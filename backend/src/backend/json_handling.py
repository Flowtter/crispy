import os
import json

from typing import Dict, Any

from utils.constants import IMAGES_PATH, JSON_PATH, MUSICS_PATH, SESSION, ASSETS
from utils.IO import io

with open(os.path.join(ASSETS, "filters.json"), "r") as js:
    filters = json.load(js)


def save_json(JSON_INFO: Dict[Any, Any]) -> None:
    with open(JSON_PATH, "w") as f:
        json.dump(JSON_INFO, f, indent=4)


def new_json() -> None:
    files = os.listdir(IMAGES_PATH)
    files.sort()
    JSON_INFO: Dict[Any, Any] = {}
    JSON_INFO["objects"] = []
    for file in files:
        if not file.endswith(".jpg"):
            continue
        obj = {}

        obj["name"] = io.remove_extension(file)
        obj["enabled"] = True
        obj["filters"] = filters
        obj["cuts"] = []

        JSON_INFO["objects"].append(obj)

    music = os.listdir(MUSICS_PATH)
    music.sort()
    JSON_INFO["musics"] = []
    for music_file in music:
        if not music_file.endswith(".mp3"):
            continue
        obj = {}

        obj["name"] = io.remove_extension(music_file)
        obj["enabled"] = True

        JSON_INFO["musics"].append(obj)

    save_json(JSON_INFO)


def load_json() -> Dict[Any, Any]:
    if not os.path.exists(SESSION):
        os.mkdir(SESSION)
    if not os.path.exists(JSON_PATH):
        new_json()

    with open(JSON_PATH, "r") as f:
        JSON_INFO = json.load(f)
    return JSON_INFO
