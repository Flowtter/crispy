import os
import random
import string
import shutil
from typing import Optional, Any, List, Tuple
import ffmpeg
from utils.constants import SETTINGS, L
from utils.filter import Filters
from PIL import Image, ImageFilter, ImageOps

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
    for frame in frames:
        start = frame[0] / frame_duration
        end = frame[1] / frame_duration
        # print(start, end, frame_duration, video_path, save_path)
        video = (
            ffmpeg
            .input(video_path)
        ) # yapf: disable
        video = apply_filter(video, video_path)

        video = video.output(os.path.join(save_path,
                                          f"{frame[0]}-{frame[1]}.mp4"),
                             ss=f"{start}",
                             to=f"{end}")
        video = video.overwrite_output()
        video.run(quiet=True)


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
        save_path = find_available_path(video_path)
        (
            ffmpeg
            .input(video_path)
            .filter("scale", w=1920, h=1080)
            .output(save_path, start_number=0)
            .overwrite_output()
            .run()
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
        save_path = find_available_path(video_path)
        (
            ffmpeg
            .input(video_path)
            .filter("scale", w=1920, h=1080)
            .output(save_path, start_number=0)
            .overwrite_output()
            .run()
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
        ) # yapf: disable
    else:
        shutil.copyfile(videos_path[0], save_path)


def apply_filter(video: ffmpeg.nodes.FilterableStream,
                 video_path: str) -> ffmpeg.nodes.FilterableStream:
    """
    Apply a list of filter to a video.
    """
    global_filters: List[Filters] = []
    for filt in SETTINGS["filters"].items():
        global_filters.append(Filters(filt[0], filt[1]))

    find_specific_filters(global_filters, video_path)
    for filt in global_filters:
        L.debug(f"Applying filter {filt.filter.name} {filt.option}")
        video = filt(video)

    return video


def find_specific_filters(global_filters: List[Filters],
                          video_path: str) -> None:
    """
    Find specificFilters for a video in Settings.json
    """
    video_name = os.path.split(video_path)
    video_name = video_name[len(video_name) - 1]
    if "clips" in SETTINGS:
        if video_name in SETTINGS["clips"]:
            for filt, value in SETTINGS["clips"][video_name].items():
                found = False
                for i in range(len(global_filters)):
                    if global_filters[i].filter.value == filt:
                        found = True
                        global_filters[i] = Filters(filt, value)
                if not found:
                    global_filters.append(Filters(filt, value))
