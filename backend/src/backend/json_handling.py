import os
import sys
import json

from typing import Dict, Any

from utils.constants import IMAGES_PATH, JSON_PATH
from utils.IO import io


def positive_hash(string: str) -> int:
    return (hash(string) + sys.maxsize + 1) % sys.maxsize


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
        obj["hash"] = positive_hash(file)
        obj["enabled"] = True

        JSON_INFO["objects"].append(obj)

    save_json(JSON_INFO)


def load_json() -> Dict[Any, Any]:
    if not os.path.exists(JSON_PATH):
        new_json()
    with open(JSON_PATH, "r") as f:
        JSON_INFO = json.load(f)
    return JSON_INFO
