import os

from starlette.config import Config

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=True)
HOST = config("HOST", default="0.0.0.0")
PORT = config("PORT", cast=int, default=1337)
MONGO_URI = config("MONGO_URI", default="mongodb://localhost/crispy")

ASSETS = "assets"
DOT_PATH = os.path.join(ASSETS, "dot.png")

BACKUP = "backup"

SESSION = "session"
RESOURCES = "resources"
VIDEOS = os.path.join(RESOURCES, "videos")

DATASET_PATH = "dataset"
DATASET_VALUES_PATH = "dataset_values.json"

DATABASE_PATH = ".data"
