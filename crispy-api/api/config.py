import json
import os

import easyocr
from starlette.config import Config

from api.tools.enums import SupportedGames

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)
HOST = config("HOST", default="127.0.0.1")
PORT = config("PORT", cast=int, default=7821)
MONGO_URI = config("MONGO_URI", default="mongodb://localhost/crispy")

ASSETS = "assets"
SILENCE_PATH = os.path.join(ASSETS, "silence.mp3")
VALORANT_MASK_PATH = os.path.join(ASSETS, "valorant-mask.png")
CSGO2_MASK_PATH = os.path.join(ASSETS, "csgo2-mask.png")

BACKUP = "backup"

SESSION = os.path.join(os.getcwd(), "session")
RESOURCES = "resources"
VIDEOS = os.path.join(RESOURCES, "videos")
MUSICS = os.path.join(RESOURCES, "musics")

DATASET_PATH = "dataset"
DATASET_VALUES_PATH = os.path.join(DATASET_PATH, "dataset-values.json")
DATASET_CSV_PATH = os.path.join(DATASET_PATH, "result.csv")
DATASET_CSV_TEST_PATH = os.path.join(DATASET_PATH, "test.csv")
NETWORK_OUTPUTS_PATH = "outputs"

DATABASE_PATH = ".data"

SETTINGS_JSON = "settings.json"

if not os.path.exists(SETTINGS_JSON):
    raise FileNotFoundError(f"{SETTINGS_JSON} not found")

with open(SETTINGS_JSON, "r") as f:
    __settings = json.load(f)

    __clip = __settings.get("clip")
    if __clip is None:
        raise KeyError(f"clips not found in {SETTINGS_JSON}")

    FRAMERATE = __clip.get("framerate", 8)
    OFFSET = __clip.get("second-between-kills", 0) * FRAMERATE
    FRAMES_BEFORE = __clip.get("second-before", 0) * FRAMERATE
    FRAMES_AFTER = __clip.get("second-after", 0) * FRAMERATE

    __neural_network = __settings.get("neural-network")
    if __neural_network is None:
        raise KeyError("neural-network not found in settings.json")

    CONFIDENCE = __neural_network.get("confidence", 0.6)

    STRETCH = __settings.get("stretch", False)
    GAME = __settings.get("game")
    if GAME is None:
        raise KeyError("game not found in settings.json")
    if GAME.upper() not in [game.name for game in SupportedGames]:
        raise ValueError(f"game {GAME} not supported")

READER = easyocr.Reader(["fr", "en"], gpu=True, verbose=False)
USE_NETWORK = GAME not in [SupportedGames.THEFINALS]
