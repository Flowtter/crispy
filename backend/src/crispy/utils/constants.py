import os

BACKEND = "backend"
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

NEURAL_NETWORK_PATH = os.path.join(ASSETS, "trained_network_latest.npy")
### CODE_PATH ###
