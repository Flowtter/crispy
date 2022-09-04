import os
import json

from typing import Dict, Any

from utils.constants import FILTERS_PATH, JSON_PATH, MUSICS_PATH, SESSION, ASSETS, TMP_PATH, VIDEOS_PATH, get_settings
from utils.IO import io

with open(os.path.join(ASSETS, "filters.json"), "r") as js:
    template_filters = json.load(js)


def save_json(JSON_INFO: Dict[Any, Any]) -> None:
    with open(JSON_PATH, "w") as f:
        json.dump(JSON_INFO, f, indent=4)


def save_filters_json(FILTERS: Dict[Any, Any]) -> None:
    with open(FILTERS_PATH, "w") as f:
        json.dump(FILTERS, f, indent=4)


def new_json() -> None:
    files = os.listdir(VIDEOS_PATH)
    files.sort()
    JSON_INFO: Dict[Any, Any] = {}
    JSON_INFO["filters"] = template_filters
    JSON_INFO["objects"] = []
    for file in files:
        if not file.endswith(".mp4"):
            continue
        obj = {}

        obj["name"] = io.remove_extension(file)
        obj["enabled"] = True
        obj["filters"] = template_filters
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

    settings = get_settings()
    JSON_INFO["game"] = settings["game"]
    save_json(JSON_INFO)


def update_json() -> None:
    with open(JSON_PATH, "r") as f:
        JSON_INFO = json.load(f)

    new_json()

    with open(JSON_PATH, "r") as f:
        NEW_JSON = json.load(f)

    settings = get_settings()
    game = settings["game"]

    if JSON_INFO["game"] != game:
        save_json(NEW_JSON)
        return

    for obj in NEW_JSON["objects"]:
        if not obj["name"] in [o["name"] for o in JSON_INFO["objects"]]:
            JSON_INFO["objects"].append(obj)
            with open(os.path.join(TMP_PATH, "recompile.json"), "w") as f:
                f.write("{\"new\":true}")

    for music in NEW_JSON["musics"]:
        if not music["name"] in [m["name"] for m in JSON_INFO["musics"]]:
            JSON_INFO["musics"].append(music)
            with open(os.path.join(TMP_PATH, "music.json"), "w") as f:
                f.write("{\"new\":true}")

    save_json(JSON_INFO)


def get_session_json() -> Dict[Any, Any]:
    if not os.path.exists(SESSION):
        os.mkdir(SESSION)
    if not os.path.exists(JSON_PATH):
        new_json()
    else:
        update_json()

    with open(JSON_PATH, "r") as f:
        JSON_INFO = json.load(f)

    return JSON_INFO
