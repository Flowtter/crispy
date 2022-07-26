from typing import List, Tuple
import os

from PIL import Image
import numpy as np

from utils.constants import TMP_PATH, IMAGE, RESOURCE_PATH, VIDEO, CUT, get_settings
import utils.ffmpeg_utils as ff
from utils.IO import io
from AI.network import NeuralNetwork


def get_saving_path(video: str) -> str:
    """
    Get the saving path for the video
    """
    return os.path.join(TMP_PATH, video, IMAGE)


def extract_frames_from_video(video: str) -> str:
    """
    Extract frames from the video
    return: saving location
    """
    SETTINGS = get_settings()

    loading_path = os.path.join(RESOURCE_PATH, VIDEO, video)

    video_no_ext = io.remove_extension(video)
    video_clean_name = io.generate_clean_name(video_no_ext)
    saving_path = os.path.join(TMP_PATH, video_clean_name, IMAGE)

    ff.extract_images(loading_path, saving_path, SETTINGS["clip"]["framerate"])

    return saving_path


def _image_to_list_format(path: str) -> List[int]:
    """
    Convert the image to list format
    """
    im = Image.open(path)
    pixel_values = list(im.getchannel("R").getdata())
    return pixel_values


def get_query_array_from_video(neural_network: NeuralNetwork,
                               images_path: str) -> List[int]:
    """
    Query the neural network on a given input
    """
    SETTINGS = get_settings()

    images = os.listdir(images_path)
    images.sort()
    query_array = []
    confidence = SETTINGS["neural-network"]["confidence"]

    for i, image in enumerate(images):
        image_path = os.path.join(images_path, image)

        list_format = _image_to_list_format(image_path)
        inputs = (np.asfarray(list_format) / 255.0 * 0.99) + 0.01

        query_result = neural_network.query(inputs)

        if query_result[1] >= confidence:
            query_array.append(i)

    return query_array


def segment_video_with_kill_array(video: str,
                                  kill_array: List[Tuple[int, int]]) -> None:
    """
    Segment the video with the given kill array
    """
    SETTINGS = get_settings()

    loading_path = os.path.join(RESOURCE_PATH, VIDEO, video)

    video_no_ext = io.remove_extension(video)
    video_clean_name = io.generate_clean_name(video_no_ext)
    save_path = os.path.join(TMP_PATH, video_clean_name, CUT)

    ff.segment_video(loading_path, save_path, kill_array,
                     SETTINGS["clip"]["framerate"])


def post_processing_kill_array(
        kill_array: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Post processing the kill array
    """
    SETTINGS = get_settings()
    found = True
    offset = SETTINGS["clip"]["second-between-kills"] * SETTINGS["clip"][
        "framerate"]
    while found:
        found = False
        for i in range(len(kill_array) - 1):
            if kill_array[i][1] + offset >= kill_array[i + 1][0]:
                found = True
                kill_array[i] = (kill_array[i][0], kill_array[i + 1][1])
                kill_array.pop(i + 1)
                break

    return kill_array


def get_kill_array_from_query_array(
        query_array: List[int]) -> List[Tuple[int, int]]:
    """
    Get the kill array from the query array
    """
    SETTINGS = get_settings()
    kill_array: List[List[int]] = []
    current_kill: List[int] = []

    framerate = SETTINGS["clip"]["framerate"]
    mul = lambda x: int(x * framerate)

    frames_before = mul(SETTINGS["clip"]["second-before"])
    frames_after = mul(SETTINGS["clip"]["second-after"])

    for q in query_array:
        if len(current_kill) == 0:
            current_kill.append(q)
        elif q - current_kill[-1] == 1:
            current_kill.append(q)
        else:
            kill_array.append(current_kill)
            current_kill = [q]
    kill_array.append(current_kill)

    result = []
    for kill in kill_array:
        # Remove fake-positives
        if len(kill) <= 2:
            continue

        start = kill[0] - frames_before
        start = max(start, 0)

        end = kill[-1] + frames_after
        result.append((start, end))
    return result


def merge_cuts() -> None:
    """
    Merge the cuts
    """
    folders = os.listdir(TMP_PATH)
    folders = [f for f in folders if os.path.isdir(os.path.join(TMP_PATH, f))]
    folders.sort()
    cuts: List[str] = []
    for folder in folders:
        cut = os.listdir(os.path.join(TMP_PATH, folder, CUT))
        cut.sort()
        for i in range(len(cut)):
            cut[i] = os.path.join(TMP_PATH, folder, CUT, cut[i])
        cuts.extend(cut)

    ff.merge_videos(cuts, "merged.mp4")


def merge_cuts_with_files(cuts: List[str], pth: str = "merged.mp4") -> None:
    """
    Merge the cuts
    """
    real_cuts = []
    for cut in cuts:
        if os.path.exists(cut):
            real_cuts.append(cut)
    ff.merge_videos(real_cuts, pth)
