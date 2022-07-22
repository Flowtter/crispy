import json
import os
import random
import string
import shutil

import datetime
from typing import Optional, Any, List, Tuple

import ffmpeg
from PIL import Image, ImageFilter, ImageOps
import cv2

from utils.constants import BACKUP, L, get_settings
from utils.filter import Filters
from utils.IO import io

BACKEND = "backend"
DOT_PATH = os.path.join(BACKEND, "assets", "dot.png")


def _apply_filter_and_do_operations(im: Image,
                                    im_filter: Optional[Any]) -> Image:

    if im_filter is not None:
        im = im.filter(im_filter)

    im = im.crop((1, 1, im.width - 2, im.height - 2))

    dot = Image.open(DOT_PATH)

    # dot = dot.resize((im.width, im.height))
    im.paste(dot, (0, 0), dot)

    left = im.crop((0, 0, 25, 60))
    right = im.crop((95, 0, 120, 60))

    final = Image.new("RGB", (50, 60))
    final.paste(left, (0, 0))
    final.paste(right, (25, 0))

    final = final.crop((00, 20, 50, 60))

    return final


def extract_images(video_path: str,
                   save_path: str,
                   framerate: int = 4) -> None:
    """
    Extract the images from the video
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    (
        ffmpeg
        .input(video_path)
        .filter("fps", fps=f"1/{round(1 / framerate, 5)}")
        .crop(x=899, y=801, width=122, height=62)
        # .overlay(ffmpeg.input(DOT_PATH))
        .output(os.path.join(save_path, "%8d.bmp"), start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable

    images = os.listdir(save_path)
    images.sort(key=lambda x: int(x.split(".")[0]))

    for im in images:
        im_path = os.path.join(save_path, im)
        im = Image.open(im_path)

        im = ImageOps.grayscale(im)

        edges = _apply_filter_and_do_operations(im, ImageFilter.FIND_EDGES)
        enhanced = _apply_filter_and_do_operations(
            im, ImageFilter.EDGE_ENHANCE_MORE)
        # im = __apply_filter_and_do_operation(im, None)

        final = Image.new("RGB", (50, 80))

        final.paste(edges, (0, 0))

        enhanced = enhanced.transpose(Image.FLIP_TOP_BOTTOM)
        final.paste(enhanced, (0, 40))

        final.save(im_path)


def segment_video(video_path: str, save_path: str,
                  frames: List[Tuple[int, int]], frame_duration: int) -> None:
    """
    Segment a video on multiple smaller video using the frames array.
    """
    video_json = []
    recompile = False
    for frame in frames:
        frame_json: dict = {"metadata": {}}
        start = frame[0] / frame_duration
        end = frame[1] / frame_duration
        frame_json["metadata"]["start"] = frame[0]
        frame_json["metadata"]["end"] = frame[1]
        frame_json["metadata"]["date"] = datetime.datetime.now().timestamp()
        frame_json["filters"] = {}
        # print(start, end, frame_duration, video_path, save_path)
        video = (
            ffmpeg
            .input(video_path)
        ) # yapf: disable
        old = video
        video, filter_json = apply_filter(video, video_path, frame_json,
                                          save_path)

        if video != old or not check_exists((frame[0], frame[1]), save_path):
            recompile = True
            video = video.output(os.path.join(save_path,
                                              f"{frame[0]}-{frame[1]}.mp4"),
                                 ss=f"{start}",
                                 to=f"{end}",
                                 preset="ultrafast")
            video = video.overwrite_output()
            video.run(quiet=True)
            L.debug(f"{frame[0]}-{frame[1]}.mp4 created or modified")
        else:
            L.debug(f"no modifications made to {frame[0]}-{frame[1]}.mp4")
            frame_json["filters"] = filter_json["filters"]

        video_json.append(frame_json)

    dir_path = os.path.split(save_path)[0]

    with open(os.path.join(dir_path, "info.json"), "r") as f:
        r = json.load(f)
        if "used" in r:
            used = r["used"]
        else:
            used = []

    with open(os.path.join(dir_path, "info.json"), "w") as f:
        json.dump({
            "recompile": recompile,
            "cuts": video_json,
            "used": used
        },
                  f,
                  indent=4,
                  sort_keys=True)


def find_available_path(video_path: str) -> str:
    """
    Find available path to store the scaled video temporarily.
    """
    dirname, basename = os.path.split(video_path)
    h = str(hash(basename)) + ".mp4"
    while (os.path.exists(os.path.join(dirname, h))):
        h = random.choice(string.ascii_letters) + h

    return os.path.join(dirname, h)


def scale_video(video_path: str) -> None:
    """
    Scale (up or down) a video.
    """
    if os.path.exists(video_path):
        vid = cv2.VideoCapture(video_path)
        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        if width == 1920 and height == 1080:
            return

        L.warning(f"\nWARNING:Scaling video {video_path}, saving a backup")

        if not os.path.exists(BACKUP):
            os.makedirs(BACKUP)

        shutil.copy(video_path,
                    os.path.join(BACKUP, os.path.basename(video_path)))

        save_path = find_available_path(video_path)
        (
            ffmpeg
            .input(video_path)
            .filter("scale", w=1920, h=1080)
            .output(save_path, start_number=0)
            .overwrite_output()
            .run(quiet=True)
        ) # yapf: disable

        os.remove(video_path)
        os.rename(save_path, video_path)
        # check if image has to be upscaled or downscaled ?
    else:
        raise FileNotFoundError(f"{video_path} not found")


def create_new_path(video_path: str) -> str:
    """
    Create new path based on the original one.
    """
    drive, tail = os.path.split(video_path)
    name, ext = os.path.splitext(tail)
    nb = 1
    cur_name = name + "_" + str(nb)
    while os.path.exists(os.path.join(drive, cur_name + ext)):
        nb = nb + 1
        cur_name = name + "_" + str(nb)

    tail = cur_name + ext
    res = os.path.join(drive, cur_name + ext)

    return res


# FIXME: audio
def merge_videos(videos_path: List[str], save_path: str) -> None:
    """
    Merge videos together.
    """
    if len(videos_path) > 1:
        videos: List[Any] = []
        for video_path in videos_path:
            videos.append(ffmpeg.input(video_path))
        (
            ffmpeg
            .concat(*videos)
            .output(save_path)
            .overwrite_output()
            .run(quiet=True)
        ) # yaPf: disable
    else:
        print("Only one video, no need to merge, copying...")
        shutil.copyfile(videos_path[0], save_path)
        print("Copy done")


def apply_filter(video: ffmpeg.nodes.FilterableStream, video_path: str,
                 frame_json: dict,
                 save_path: str) -> ffmpeg.nodes.FilterableStream:
    """
    Apply a list of filter to a video.
    """
    global_filters: List[Filters] = find_filters(video_path)
    start = frame_json["metadata"]["start"]
    end = frame_json["metadata"]["end"]

    check, json_ = check_recompile(save_path, (start, end), global_filters)
    if not check:
        return video, json_

    for filt in global_filters:
        old = video
        video = filt(video)
        if old != video:
            L.debug(f"Applying filter {filt.filter.name} {filt.option}")
            frame_json["filters"][filt.filter.value] = filt.option

    return video, json_


def find_filters(video_path: str) -> List[Filters]:
    SETTINGS = get_settings()
    global_filters: List[Filters] = []
    if "filters" in SETTINGS:
        for filt in SETTINGS["filters"].items():
            global_filters.append(Filters(filt[0], filt[1]))

    video_name = os.path.split(video_path)[-1]
    no_ext = io.remove_extension(video_name)
    if "clips" in SETTINGS:
        if no_ext in SETTINGS["clips"]:
            for filt, value in SETTINGS["clips"][no_ext].items():
                found = False
                for i in range(len(global_filters)):
                    if global_filters[i].filter.value == filt:
                        found = True
                        global_filters[i] = Filters(filt, value)
                if not found:
                    global_filters.append(Filters(filt, value))
    return global_filters


def check_exists(frame: Tuple[int, int], save_path: str) -> bool:
    """
    Check if the clip already exists
    """
    dir_path = os.path.split(save_path)[0]
    path = os.path.join(dir_path, "info.json")
    if not os.path.exists(path):
        return False
    with open(path) as f:
        video_json = json.load(f)["cuts"]
    for clip in video_json:
        if clip["metadata"]["start"] == frame[0] and clip["metadata"][
                "end"] == frame[1]:
            return True
    return False


def check_recompile(save_path: str, frame: Tuple[int, int],
                    filter_list: List[Filters]) -> Tuple[bool, dict]:
    """
    Check if modifications has to be done to a video
    True if has to recompile, False otherwise
    """
    dir_path = os.path.split(save_path)[0]
    path = os.path.join(dir_path, "info.json")
    if not os.path.exists(path):
        return True, {}
    with open(os.path.join(dir_path, "info.json")) as f:
        video_json = json.load(f)["cuts"]

    count = 0
    clip: dict = {}

    if not check_exists(frame, save_path):
        return True, {}

    for clip_json in video_json:
        if clip_json["metadata"]["start"] == frame[0] and clip_json[
                "metadata"]["end"] == frame[1]:
            clip = clip_json
    length = len(clip["filters"])

    for filt in filter_list:
        if filt.filter.value in clip["filters"]:
            if filt.option != clip["filters"][filt.filter.value]:
                # filter different, video has to be recompiled
                return True, clip
            count += 1
        elif type(filt.option) == bool and not filt.option:
            continue
        else:
            return True, clip

    if count == length:
        return False, clip
    return True, clip
