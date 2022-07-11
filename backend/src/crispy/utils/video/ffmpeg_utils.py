import os
import random
import string
from typing import Optional, Any

import ffmpeg
from PIL import Image, ImageFilter, ImageOps

BACKEND = "backend"
DOT_PATH = os.path.join(BACKEND, "assets", "dot.png")


def __apply_filter_and_do_operations(im: Image,
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


def extract_images(video_path: str, save_path: str) -> None:
    """Extract the images from the video"""
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    (
        ffmpeg
        .input(video_path)
        .filter('fps', fps='1/0.25')
        .crop(x=899, y=801, width=122, height=62)
        # .overlay(ffmpeg.input(DOT_PATH))
        .output(os.path.join(save_path, "%5d.bmp"), start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable

    images = os.listdir(save_path)
    images.sort(key=lambda x: int(x.split(".")[0]))

    for im in images:
        im_path = os.path.join(save_path, im)
        im = Image.open(im_path)

        im = ImageOps.grayscale(im)

        edges = __apply_filter_and_do_operations(im, ImageFilter.FIND_EDGES)
        enhanced = __apply_filter_and_do_operations(
            im, ImageFilter.EDGE_ENHANCE_MORE)
        # im = __apply_filter_and_do_operation(im, None)

        final = Image.new("RGB", (50, 80))

        final.paste(edges, (0, 0))

        enhanced = enhanced.transpose(Image.FLIP_TOP_BOTTOM)
        final.paste(enhanced, (0, 40))

        final.save(im_path)


def find_available_path(video_path: str) -> str:
    """
    Find available path to store the scaled video temporarily.
    """
    drive, tail = os.path.split(video_path)
    tail = random.choice(string.ascii_letters) + tail
    while (os.path.exists(os.path.join(drive, tail))):
        tail = random.choice(string.ascii_letters) + tail

    return os.path.join(drive, tail)


def scale_video(video_path: str) -> None:
    """
    Scale (up or down) a video.
    """
    if os.path.exists(video_path):
        save_path = find_available_path(video_path)
        (
            ffmpeg
            .input(video_path)
            .filter('scale', w=1920, h=1080)
            .output(save_path, start_number=0)
            .overwrite_output()
            .run(quiet=True)
        ) # yapf: disable

        os.remove(video_path)
        os.rename(save_path, video_path)
        # check if image has to be upscaled or downscaled ?


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


def split_video_once(video_path: str, split: tuple) -> None:
    """
    Split a video between 2 timestamp
    """
    save_path = create_new_path(video_path)
    if split[1] - split[0] > 0:
        (
            ffmpeg
            .input(video_path)
            .trim(start_frame=split[0], end_frame=split[1])
            .output(save_path)
            .overwrite_output()
            .run(quiet=True)
        ) # yapf: disable


def split_video(video_path: str, splits: list) -> None:
    if os.path.exists(video_path):
        for split in splits:
            split_video_once(video_path, split)
