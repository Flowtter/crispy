import os

import ffmpeg

BACKEND = "backend"
DOT_PATH = os.path.join(BACKEND, "assets", "dot.png")


def extract_images(video_path: str, save_path: str) -> None:
    """Extract the images from the video"""
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    (
        ffmpeg
        .input(video_path)
        .filter('fps', fps='1/0.25')
        .crop(x=900, y=804, width=120, height=60)
        .overlay(ffmpeg.input(DOT_PATH))
        .output(os.path.join(save_path, "%3d.bmp"), start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable
