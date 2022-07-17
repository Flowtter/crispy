import os
import json
import sys

from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# FIXME: Refactor most of this code
# Most routes are poorly named and not very descriptive

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIRECTORY_PATH = "resources"
DIRECTORY_IMAGE = os.path.join(DIRECTORY_PATH, "image")
DIRECTORY_VIDEO = os.path.join(DIRECTORY_PATH, "video")
DIRECTORY_FRONTEND_VIDEO = os.path.join(DIRECTORY_PATH, "frontend_video")

SESSION = "session"
JSON_PATH = os.path.join(SESSION, "info.json")
JSON_INFO = None


# TODO: check that ffmpeg is installed firstly
@app.on_event("startup")
def main() -> None:
    if not os.path.exists(SESSION):
        os.makedirs(SESSION)
    new_json()

    # -----------------------------------------
    # FIXME: Generate thumnails for all images
    # FIXME: Generate smaller videos for all videos
    # SEE: https://github.com/Flowtter/crispy-2/blob/6cea6f5d2fcfdf541d8e56d30a0d6feca12f235c/backend/src/app.py
    # TODO: use the ffmpeg-python library /!\ /!\ /!\
    # -----------------------------------------


def positive_hash(string: str) -> int:
    return (hash(string) + sys.maxsize + 1) % sys.maxsize


def save_json() -> None:
    with open(JSON_PATH, "w") as f:
        json.dump(JSON_INFO, f)


def new_json() -> None:
    global JSON_INFO
    files = os.listdir(DIRECTORY_IMAGE)
    JSON_INFO = {}
    JSON_INFO["images"] = []
    for file in files:
        if file.endswith(".gitkeep"):
            continue
        info = {}
        # FIXME: shouldnt use the `.png` extension in the "name" field
        info["name"] = file
        info["hash"] = positive_hash(file)
        info["enabled"] = True
        # FIXME: should be "object" instead of images
        JSON_INFO["images"].append(info)
    JSON_INFO["music"] = {}
    JSON_INFO["music"]["enabled"] = False
    JSON_INFO["music"]["volume"] = 0.5
    JSON_INFO["music"]["bpm"] = None

    save_json()


@app.get("/")
async def main_root():
    return JSON_INFO


# TODO: Create a route "object" instead of "images"
# FIXME: This route shouldnt be in /images but in /objects/{filename}/image
@app.get("/images/{filename}")
async def get_image(filename):
    return FileResponse(os.path.join(DIRECTORY_IMAGE, filename))


# FIXME: This route shouldnt be in /images but in /objects/{filename}/info
@app.get("/images/{filename}/info")
async def get_image_info(filename):
    images = JSON_INFO["images"]
    image = next(filter(lambda x: x["name"] == filename, images), None)
    return image


# FIXME: This route shouldnt be in /images but in /objects/{filename}/swap-order
@app.get("/images/{filename}/switch")
async def switch(filename):
    images = JSON_INFO["images"]
    image = next(filter(lambda x: x["name"] == filename, images), None)
    index = images.index(image)

    image["enabled"] = not image["enabled"]
    images[index] = image

    JSON_INFO["images"] = images

    save_json()

    return image["enabled"]


@app.get("/reload")
async def reload():
    new_json()
    save_json()
    return JSON_INFO


class Reorder(BaseModel):
    """DTO for reordering images"""
    name: str


@app.post("/reorder")
async def reorder(data: List[Reorder]):
    images = JSON_INFO["images"]
    new_images = []
    for datum in data:
        image = next(filter(lambda x: x["name"] == datum.name, images), None)
        new_images.append(image)
    JSON_INFO["images"] = new_images

    save_json()
    return JSON_INFO


@app.get("/send")
async def send():
    return "Send"


@app.get("/status")
async def status():
    return "Not implemented"
