import os
import cv2
from pytube import YouTube
from ffmpeg_utils import scale_video


def test_basic() -> None:
    os.mkdir("./test_mp4")
    yt = YouTube("https://www.youtube.com/watch?v=6A-hTKYBkC4")
    yt.streams.order_by("resolution").desc().first().download(
        filename="./test_mp4/test_basic.mp4")
    vid = cv2.VideoCapture("./test_mp4/test_basic.mp4")
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    os.remove("./test_mp4/test_basic.mp4")
    assert width == 1920 and height == 1080


def test_upscale() -> None:
    yt = YouTube("https://www.youtube.com/watch?v=6A-hTKYBkC4")
    yt.streams.order_by("resolution").asc().first().download(
        filename="./test_mp4/test_upscale.mp4")

    scale_video("./test_mp4/test_upscale.mp4")
    vid = cv2.VideoCapture("./test_mp4/test_upscale.mp4")
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    os.remove("./test_mp4/test_upscale.mp4")
    assert width == 1920 and height == 1080


def test_downscale() -> None:
    yt = YouTube("https://www.youtube.com/watch?v=wZI9is9Ix90")
    yt.streams.order_by("resolution").desc().first().download(
        filename="./test_mp4/test_downscale.mp4")

    scale_video("./test_mp4/test_downscale.mp4")
    vid = cv2.VideoCapture("./test_mp4/test_downscale.mp4")
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    os.remove("./test_mp4/test_downscale.mp4")
    os.rmdir("./test_mp4")
    assert width == 1920 and height == 1080


def abort(video_path: str) -> None:
    top = os.path.split(video_path)[0]
    print(top)
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)


def split_check(video_path: str, frames: int) -> bool:
    drive = os.path.split(video_path)[0]
    for f in os.listdir():
        path = os.path.join(drive, f)
        if os.path.isfile(os.path.join(drive, f)):
            vid = cv2.VideoCapture(path)
            fps = vid.get(cv2.CAP_PROP_FPS)
            frame_count = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count // fps

            print(duration)
            if duration != frames:
                abort(video_path)
                return False
    return True
