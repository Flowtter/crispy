import os
import logging
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

L = logging.getLogger("crispy")

logging.getLogger("PIL").setLevel(logging.ERROR)

BACKEND = "backend"
FRONTEND = "frontend"
OUTPUT = "output"

### UTILS ###
VIDEO = "video"
MUSIC = "music"
IMAGE = "image"
CUT = "cut"
### UTILS ###

### DATASET_PATH ###
DATASET_PATH = os.path.join(BACKEND, "dataset")
ASSETS = os.path.join(BACKEND, "assets")

DATASET_VALUES_PATH = os.path.join(DATASET_PATH, "values.json")
DOT_PATH = os.path.join(ASSETS, "dot.png")
### DATASET_PATH ###

### CODE_PATH ###
GLOBAL_PATH = BACKEND  #FIXME: This is a temporary solution

TMP_PATH = os.path.join(GLOBAL_PATH, "tmp")

RESOURCE_PATH = os.path.join(GLOBAL_PATH, "resources")
VIDEOS_PATH = os.path.join(RESOURCE_PATH, VIDEO)
MUSICS_PATH = os.path.join(RESOURCE_PATH, MUSIC)

IMAGES_PATH = os.path.join(TMP_PATH, IMAGE)
FRONTEND_PATH = os.path.join(TMP_PATH, FRONTEND)

NEURAL_NETWORK_PATH = os.path.join(ASSETS, "trained_network_latest.npy")
### CODE_PATH ###

### SETTINGS ###
SETTINGS_PATH = "settings.json"
_f = open(SETTINGS_PATH, "r")
SETTINGS = json.load(_f)
_f.close()
### SETTINGS ###

### BACKEND ###
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSION = "session"
JSON_PATH = os.path.join(SESSION, "info.json")
###