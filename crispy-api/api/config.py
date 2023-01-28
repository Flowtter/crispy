import os

from starlette.config import Config

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=True)
HOST = config("HOST", default="127.0.0.1")
PORT = config("PORT", cast=int, default=7821)
MONGO_URI = config("MONGO_URI", default="mongodb://localhost/crispy")

ASSETS = "assets"
DOT_PATH = os.path.join(ASSETS, "dot.png")

BACKUP = "backup"

SESSION = os.path.join(os.getcwd(), "session")
RESOURCES = "resources"
VIDEOS = os.path.join(RESOURCES, "videos")
MUSICS = os.path.join(RESOURCES, "musics")

DATASET_PATH = "dataset"
DATASET_VALUES_PATH = "dataset_values.json"

DATABASE_PATH = ".data"
