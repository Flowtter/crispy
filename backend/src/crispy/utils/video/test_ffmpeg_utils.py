import os
import cv2
from pytube import YouTube
from ffmpeg_utils import scale_video, split_video


def test_basic() -> None:
    os.mkdir('./test_mp4')
    yt = YouTube('https://www.youtube.com/watch?v=6A-hTKYBkC4')
    yt.streams.order_by('resolution').desc().first().download(
        filename='./test_mp4/test_basic.mp4')
    vid = cv2.VideoCapture('./test_mp4/test_basic.mp4')
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    os.remove('./test_mp4/test_basic.mp4')
    assert width == 1920 and height == 1080


def test_upscale() -> None:
    yt = YouTube('https://www.youtube.com/watch?v=6A-hTKYBkC4')
    yt.streams.order_by('resolution').asc().first().download(
        filename='./test_mp4/test_upscale.mp4')

    scale_video('./test_mp4/test_upscale.mp4')
    vid = cv2.VideoCapture('./test_mp4/test_upscale.mp4')
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    os.remove('./test_mp4/test_upscale.mp4')
    assert width == 1920 and height == 1080


def test_downscale() -> None:
    yt = YouTube('https://www.youtube.com/watch?v=wZI9is9Ix90')
    yt.streams.order_by('resolution').desc().first().download(
        filename='./test_mp4/test_downscale.mp4')

    scale_video('./test_mp4/test_downscale.mp4')
    vid = cv2.VideoCapture('./test_mp4/test_downscale.mp4')
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    os.remove('./test_mp4/test_downscale.mp4')
    os.rmdir('./test_mp4')
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


def cut_1_100(video_path: str) -> bool:
    split_video(video_path, [(0, 100)])
    return split_check(video_path, 100)


def cut_10_100(video_path: str) -> bool:
    split_video(video_path, [(0, 100), (100, 200), (200, 300), (300, 400),
                             (400, 500), (500, 600), (600, 700), (700, 800),
                             (800, 900), (900, 1000)])
    return split_check(video_path, 100)


def test_split() -> None:
    os.mkdir('test_split')
    yt = YouTube('https://www.youtube.com/watch?v=6A-hTKYBkC4')
    yt.streams.order_by('resolution').desc().first().download(
        filename='./test_split/test_basic.mp4')

    assert cut_1_100('./test_split/test_basic.mp4')

    yt.streams.order_by('resolution').desc().first().download(
        filename='./test_split/test_basic.mp4')
    assert cut_10_100('./test_split/test_basic.mp4')

    abort('./test_split/tset_basic.mp4')