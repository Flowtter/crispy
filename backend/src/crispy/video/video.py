from typing import List, Tuple
import os

from PIL import Image
import numpy as np

from utils.constants import TMP_PATH, IMAGE, RESOURCE_PATH, VIDEO, CUT
import utils.ffmpeg_utils as ff
from utils.IO import io
from AI.network import NeuralNetwork


def get_saving_path(video: str) -> str:
    """
    Get the saving path for the video
    """
    return os.path.join(TMP_PATH, video, IMAGE)


def extract_frames_from_video(video: str, framerate: int = 6) -> str:
    """
    Extract frames from the video
    return: saving location
    """
    loading_path = os.path.join(RESOURCE_PATH, VIDEO, video)

    video_no_ext = io.remove_extension(video)
    video_clean_name = io.generate_clean_name(video_no_ext)
    saving_path = os.path.join(TMP_PATH, video_clean_name, IMAGE)

    ff.extract_images(loading_path, saving_path, framerate)

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
    images = os.listdir(images_path)
    images.sort()
    query_array = []

    for i, image in enumerate(images):
        image_path = os.path.join(images_path, image)

        list_format = _image_to_list_format(image_path)
        inputs = (np.asfarray(list_format) / 255.0 * 0.99) + 0.01

        query_result = neural_network.query(inputs)

        # FIXME: confidence is not used
        # Should be used instead of np.argmax
        result = np.argmax(query_result)

        if result == 1:
            query_array.append(i)

    return query_array


def segment_video_with_kill_array(video: str,
                                  kill_array: List[Tuple[int, int]],
                                  frame_duration: int = 4) -> None:
    """
    Segment the video with the given kill array
    """

    loading_path = os.path.join(RESOURCE_PATH, VIDEO, video)

    video_no_ext = io.remove_extension(video)
    video_clean_name = io.generate_clean_name(video_no_ext)
    save_path = os.path.join(TMP_PATH, video_clean_name, CUT)

    ff.segment_video(loading_path, save_path, kill_array, frame_duration)


# FIXME: Add post processing
def get_kill_array_from_query_array(
        query_array: List[int], frames_before: int,
        frames_after: int) -> List[Tuple[int, int]]:
    """
    Get the kill array from the query array
    """
    kill_array: List[List[int]] = []
    current_kill: List[int] = []
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
        start = kill[0] - frames_before
        end = kill[-1] + frames_after
        result.append((start, end))

    return result
