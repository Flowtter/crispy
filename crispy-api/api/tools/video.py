import asyncio
import logging
import os
from typing import List, Tuple

import numpy as np
from PIL import Image

from api.config import GAME, READER
from api.models.highlight import Highlight
from api.models.segment import Segment
from api.tools.AI.network import NeuralNetwork
from api.tools.enums import SupportedGames

logger = logging.getLogger("uvicorn")


def _image_to_list_format(path: str) -> List[int]:
    """
    Convert the image to list format

    :param path: path to the image

    :return: list of the image
    """
    return list(Image.open(path).getchannel("R").getdata())


def _create_query_array(
    neural_network: NeuralNetwork, highlight: Highlight, confidence: float
) -> List[int]:
    """
    Query the neural network on a given input

    :param neural_network: neural network to query
    :param highlight: highlight to query
    :param confidence: confidence to query

    :return: list of the query
    """
    images = os.listdir(highlight.images_path)
    images.sort()
    queries = []

    for i, image in enumerate(images):
        image_path = os.path.join(highlight.images_path, image)

        list_format = _image_to_list_format(image_path)
        inputs = (np.asfarray(list_format) / 255.0 * 0.99) + 0.01

        query = neural_network.query(inputs)

        if query[1] >= confidence:
            queries.append(i)

    return queries


def _create_the_finals_query_array(highlight: Highlight) -> List[int]:
    usernames = highlight.usernames
    images = os.listdir(highlight.images_path)
    images.sort()
    queries = []

    for i, image in enumerate(images):
        image_path = os.path.join(highlight.images_path, image)

        text = READER.readtext(image_path)
        for word in text:
            if word[1] not in usernames:
                queries.append(i)
                break

    return queries


def _get_query_array(
    neural_network: NeuralNetwork, highlight: Highlight, confidence: float
) -> List[int]:
    if neural_network:
        return _create_query_array(neural_network, highlight, confidence)
    if GAME == SupportedGames.THEFINALS:
        return _create_the_finals_query_array(highlight)
    raise ValueError(f"No neural network for game {GAME} and no custom query array")


def _normalize_queries(
    queries: List[int], frames_before: int, frames_after: int
) -> List[Tuple[int, int]]:
    """
    Normalize the query array

    :param queries: query array to normalize
    :param frames_before: number of frames before the kill
    :param frames_after: number of frames after the kill

    :return: normalized query array
    """
    normalize: List[List[int]] = []
    current: List[int] = []

    for query in queries:
        if len(current) == 0 or query - current[-1] == 1:
            current.append(query)
        else:
            normalize.append(current)
            current = [query]
    normalize.append(current)

    result = []
    for kill in normalize:
        # Remove false-positives
        if len(kill) <= 2:
            continue

        start = kill[0] - frames_before
        start = max(start, 0)

        end = kill[-1] + frames_after
        result.append((start, end))
    return result


def _post_process_query_array(
    queries: List[Tuple[int, int]], offset: int, framerate: int
) -> List[Tuple[float, float]]:
    """
    Post processing the kill array using frame for time unit

    :param queries: kill array to post process
    :param offset: offset to post process

    :return: post processed kill array using seconds for time unit
    """
    found = True
    while found:
        found = False
        for i in range(len(queries) - 1):
            if queries[i][1] + offset >= queries[i + 1][0]:
                found = True
                queries[i] = (queries[i][0], queries[i + 1][1])
                queries.pop(i + 1)
                break

    return [(start / framerate, end / framerate) for start, end in queries]


async def extract_segments(
    highlight: Highlight,
    neural_network: NeuralNetwork,
    confidence: float,
    framerate: int,
    offset: int,
    frames_before: int,
    frames_after: int,
) -> Tuple[List[Tuple[float, float]], List[Segment]]:
    """
    Extract segments from a highlight

    :param highlight: highlight to extract segments from
    :param confidence: confidence to query
    :param offset: offset to post process
    :param framerate: framerate of the video

    :return: list of segments
    """
    queries = _get_query_array(neural_network, highlight, confidence)
    normalized = _normalize_queries(queries, frames_before, frames_after)
    processed = _post_process_query_array(normalized, offset, framerate)
    segments = await highlight.extract_segments(processed)

    coroutines = []
    for segment in segments:
        coroutines.append(segment.copy_video_in_lower_resolution())
    await asyncio.gather(*coroutines)

    return (processed, segments)
