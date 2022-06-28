import subprocess
from typing import List
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from threading import Thread

from dotenv import load_dotenv

import os
import json
import sys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = load_dotenv()

DIRECTORY_PATH = os.getenv("DIRECTORY_PATH")
DIRECTORY_IMAGE = os.path.join(DIRECTORY_PATH, "image")
DIRECTORY_VIDEO = os.path.join(DIRECTORY_PATH, "video")
DIRECTORY_FRONTEND_VIDEO = os.path.join(DIRECTORY_PATH, "frontend_video")

SESSION = os.getenv("APP") + "session"
JSON_PATH = os.path.join(SESSION, "info.json")
JOB_PATH = os.path.join(SESSION, "job.json")
json_info = None


@app.on_event("startup")
def main():
    global json_info

    if not os.path.exists(SESSION):
        os.makedirs(SESSION)

    new_json()


def thumbnail():
    files = os.listdir(DIRECTORY_VIDEO)

    if not os.path.exists(DIRECTORY_IMAGE):
        os.makedirs(DIRECTORY_IMAGE)

    for file in files:
        if file.endswith(".gitkeep"):
            continue
        video_path = os.path.join(DIRECTORY_VIDEO, file)
        image_path = os.path.join(DIRECTORY_IMAGE, file[:-4] + ".png")
        os.system(
            f"ffmpeg -y -i '{video_path}' -ss 00:00:00 -vframes 1 '{image_path}' 2> /dev/null"
        )


def downscale_videos():
    files = os.listdir(DIRECTORY_VIDEO)
    threads = []

    if not os.path.exists(DIRECTORY_FRONTEND_VIDEO):
        os.makedirs(DIRECTORY_FRONTEND_VIDEO)

    for file in files:
        if file.endswith(".gitkeep"):
            continue
        video_path = os.path.join(DIRECTORY_VIDEO, file)
        output_path = os.path.join(DIRECTORY_FRONTEND_VIDEO, file)
        if not os.path.exists(output_path):
            threads.append(
                Thread(
                    target=os.system,
                    args=
                    (f"ffmpeg -i '{video_path}' -vf scale=320:240 '{output_path}' 2> /dev/null",
                     )))

    for thread in threads:
        thread.start()

    print("Downscaling videos ... it might take a while")
    for thread in threads:
        thread.join()


def positive_hash(string):
    return (hash(string) + sys.maxsize + 1) % sys.maxsize


def save_json():
    with open(JSON_PATH, "w") as f:
        json.dump(json_info, f)


def new_json():
    global json_info
    thumbnail()
    downscale_videos()
    files = os.listdir(DIRECTORY_IMAGE)
    with open(JSON_PATH, "w") as f:
        json_info = dict()
        json_info["images"] = []
        for file in files:
            if file.endswith(".gitkeep"):
                continue
            info = dict()
            info["name"] = file
            info["hash"] = positive_hash(file)
            info["enabled"] = True
            json_info["images"].append(info)
        json_info["music"] = dict()
        json_info["music"]["enabled"] = False
        json_info["music"]["volume"] = 0.5
        json_info["music"]["bpm"] = None


@app.get('/')
async def main_root():
    return json_info


@app.get("/images/{filename}")
async def get_image(filename):
    return FileResponse(os.path.join(DIRECTORY_IMAGE, filename))


@app.get("/images/{filename}/info")
async def get_image(filename):
    images = json_info["images"]
    image = next(filter(lambda x: x["name"] == filename, images), None)
    return image


@app.get("/images/{filename}/switch")
async def get_image(filename):
    global json_info
    images = json_info["images"]
    image = next(filter(lambda x: x["name"] == filename, images), None)
    index = images.index(image)

    image["enabled"] = not image["enabled"]
    images[index] = image

    json_info["images"] = images

    save_json()

    return image["enabled"]


@app.get("/reload")
async def reload():
    new_json()
    save_json()
    return json_info


class Reorder(BaseModel):
    name: str


@app.post("/reorder")
async def reorder(data: List[Reorder]):
    global json_info
    images = json_info["images"]
    new_images = []
    for datum in data:
        image = next(filter(lambda x: x["name"] == datum.name, images), None)
        new_images.append(image)
    json_info["images"] = new_images

    save_json()
    return json_info


instance = None


@app.get("/send")
async def send():
    try:
        with open(JOB_PATH, 'w') as outfile:
            res = dict()
            res["count"] = 0
            res["max"] = 1
            res["job"] = "starting"
            json.dump(res, outfile)
        global instance
        if instance != None:
            print("killing instance")
            # kill the os.system
            instance.terminate()
        instance = subprocess.Popen(
            ["python3", os.getcwd() + "/src/crispy/main.py"])
    except Exception as e:
        print("error:", e)


# could be not async to load them one by one
@app.get("/video/{filename}")
async def get_video(filename):
    filename = filename[:-4] + ".mp4"
    return FileResponse(os.path.join(DIRECTORY_FRONTEND_VIDEO, filename))


@app.get("/export/video")
async def get_video():
    return FileResponse("export.mp4")


@app.get("/export/image")
async def get_video():
    os.system(
        f"ffmpeg -y -i export.mp4 -ss 00:00:00 -vframes 1 export.png 2> /dev/null"
    )

    return FileResponse("export.png")


@app.get("/status")
async def status():
    try:
        with open(JOB_PATH, "r") as f:
            return json.load(f)
    except:
        return None
