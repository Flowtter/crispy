import os

import ffmpeg
import progressbar

from utils.constants import FRONTEND_PATH, SESSION, app, L, VIDEOS_PATH, IMAGES_PATH
from utils.IO import io

from backend.json_handling import new_json, load_json


def extract_first_image_of_video(video_path: str, output: str) -> None:
    """Extract the first image of a video"""
    video = ffmpeg.input(video_path)
    image = video.output(f"{output}.jpg", vframes=1)
    image.run(quiet=True)


def extract_first_seconds_in_240p(video_path: str, output: str) -> None:
    """Extract the 5 first secondes of a video"""
    try:
        video = ffmpeg.input(video_path, sseof="-20")
        video = video.filter("scale", w=240, h=180)
        video = video.output(f"{output}.mp4", t="00:00:10")
        video.run(quiet=True)
    except ffmpeg.Error as e:
        L.error(f"For video {video_path}, ffmpeg error: {e}")
        video = ffmpeg.input(video_path)
        video = video.filter("scale", w=240, h=180)
        video = video.output(f"{output}.mp4")
        video.run(quiet=True)


# TODO: check that ffmpeg is installed firstly
@app.on_event("startup")
def startup() -> None:
    files = os.listdir(VIDEOS_PATH)
    files.sort()

    if not os.path.exists(FRONTEND_PATH):
        os.mkdir(FRONTEND_PATH)

    if not os.path.exists(SESSION):
        os.mkdir(SESSION)
        new_json()
    else:
        load_json()

    print(
        "Extracting thumbnails and snippets, might take a while if it's the first time you start the program..."
    )
    progress = progressbar.ProgressBar(max_value=len(files))
    for i, file in enumerate(files):
        progress.update(i)
        no_ext = io.remove_extension(file)
        im = os.path.join(IMAGES_PATH, no_ext)
        snip = os.path.join(FRONTEND_PATH, no_ext)

        if not os.path.exists(im + ".jpg"):
            extract_first_image_of_video(os.path.join(VIDEOS_PATH, file), im)
        if not os.path.exists(snip + ".mp4"):
            extract_first_seconds_in_240p(os.path.join(VIDEOS_PATH, file),
                                          snip)
    progress.finish()
