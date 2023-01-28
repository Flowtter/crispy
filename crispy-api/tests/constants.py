import os

ROOT_ASSETS = os.path.join("tests", "assets")
VIDEOS_PATH = os.path.join(ROOT_ASSETS, "videos")
MUSICS_PATH = os.path.join(ROOT_ASSETS, "musics")
CSV_PATH = os.path.join(ROOT_ASSETS, "csv")

MAIN_MUSIC = os.path.join(MUSICS_PATH, "trumpet.mp3")

MAIN_VIDEO = os.path.join(VIDEOS_PATH, "main-video.mp4")
MAIN_VIDEO_NO_AUDIO = os.path.join(VIDEOS_PATH, "main-video-no-audio.mp4")
MAIN_VIDEO_OVERWATCH = os.path.join(VIDEOS_PATH, "main-video-overwatch.mp4")

DATASET_VALUES_PATH = os.path.join(ROOT_ASSETS, "dataset_values.json")

CSV_PATH_XOR = os.path.join(CSV_PATH, "xor.csv")
CSV_PATH_OVERWATCH = os.path.join(CSV_PATH, "overwatch.csv")

OVERWATCH_NETWORK = os.path.join("assets", "overwatch.npy")
VALORANT_NETWORK = os.path.join("assets", "valorant.npy")
