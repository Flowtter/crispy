import os
import sys
import json

from utils.constants import IMAGES_PATH, JSON_PATH, JSON_INFO
from utils.IO import io


def positive_hash(string: str) -> int:
    return (hash(string) + sys.maxsize + 1) % sys.maxsize


def save_json() -> None:
    with open(JSON_PATH, "w") as f:
        json.dump(JSON_INFO, f, indent=4)


def new_json() -> None:
    global JSON_INFO
    files = os.listdir(IMAGES_PATH)
    files.sort()
    JSON_INFO = {}
    JSON_INFO["objects"] = []
    for file in files:
        if not file.endswith(".jpg"):
            continue
        obj = {}

        obj["name"] = io.remove_extension(file)
        obj["hash"] = positive_hash(file)
        obj["enabled"] = True

        JSON_INFO["objects"].append(obj)
    save_json()


def load_json() -> None:
    global JSON_INFO
    with open(JSON_PATH, "r") as f:
        JSON_INFO = json.load(f)
