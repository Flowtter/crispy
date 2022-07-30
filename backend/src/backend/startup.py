import os
import time

import ffmpeg
import progressbar

from utils.constants import app, L, FRONTEND_PATH, VIDEOS_PATH, IMAGES_PATH, TMP_PATH
from utils.IO import io
import utils.ffmpeg_utils as ff
import video.video as vid
from PIL import Image


def extract_first_image_of_video(video_path: str, output: str) -> None:
    """Extract the first image of a video"""
    video = ffmpeg.input(video_path)
    image = video.output(f"{output}.jpg", vframes=1)
    image = image.overwrite_output()
    image.run(quiet=True)


def extract_snippet_in_lower_res(video_path: str, output: str) -> None:
    """Extract the 5 first secondes of a video"""
    w, h = 640, 360
    try:
        video = ffmpeg.input(video_path, sseof="-20")
        video = video.filter("scale", w=w, h=h)
        video = video.output(f"{output}.mp4", t="00:00:10")
        video.run(quiet=True)
    except ffmpeg.Error as e:
        L.error(f"For video {video_path}, ffmpeg error: {e}")
        video = ffmpeg.input(video_path)
        video = video.filter("scale", w=w, h=h)
        video = video.output(f"{output}.mp4")
        video.run(quiet=True)


def check_image_is_1080p(image_path: str) -> bool:
    size = Image.open(image_path).size
    return size[0] == 1920 and size[1] == 1080


# TODO: check that ffmpeg is installed firstly
@app.on_event("startup")
def startup() -> None:
    files = os.listdir(VIDEOS_PATH)
    files.sort()

    if not os.path.exists(TMP_PATH):
        os.mkdir(TMP_PATH)
    if not os.path.exists(FRONTEND_PATH):
        os.mkdir(FRONTEND_PATH)
    if not os.path.exists(IMAGES_PATH):
        os.mkdir(IMAGES_PATH)

    print("Extracting thumbnails, snippets and frames")
    print("This may take a while if it's the first time you run the app")

    if len(files) > 70:
        print(
            "Due to some browser restrictions, having more than 70 clips may produce errors"
        )
        time.sleep(3)

    progress = progressbar.ProgressBar(max_value=len(files))

    for i, file in enumerate(files):
        if not file.endswith(".mp4"):
            continue
        video = os.path.join(VIDEOS_PATH, file)

        progress.update(i)
        no_ext = io.remove_extension(file)
        im = os.path.join(IMAGES_PATH, no_ext)
        snip = os.path.join(FRONTEND_PATH, no_ext)

        # check that the video is in 1080p
        extract_first_image_of_video(video, im)
        if not check_image_is_1080p(im + ".jpg"):
            # convert if not the case (old video saved in /backup)
            ff.scale_video(video)

        # create a snippet of the video
        if not os.path.exists(snip + ".mp4"):
            extract_snippet_in_lower_res(video, snip)

        # create a thumbnail of the snippet
        extract_first_image_of_video(snip + ".mp4", im)

        # extract frame of the 1080p video
        video_clean_name = io.generate_clean_name(no_ext)
        if not os.path.exists(os.path.join(TMP_PATH, video_clean_name)):
            io.generate_folder_clip(video_clean_name)
            vid.extract_frames_from_video(file)

    progress.finish()
