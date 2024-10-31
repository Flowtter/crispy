import asyncio
import logging
import os
from collections import Counter
from typing import Any, Dict, List, Tuple, Union

import cv2
import numpy as np
from PIL import Image

from api.config import GAME, LEAGUE_IMAGES_PATH, READER
from api.models.highlight import Highlight
from api.models.segment import Segment
from api.tools.AI.network import NeuralNetwork
from api.tools.enums import SupportedGames
from api.tools.utils import levenstein_distance

logger = logging.getLogger("uvicorn")

LEAGUE_CHAMPIONS: List[Dict[str, Any]] = []


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
    teammate_usernames = highlight.usernames
    images = os.listdir(highlight.images_path)
    images.sort()

    usernames_histogram: Counter = Counter()

    for image in images:
        image_path = os.path.join(highlight.images_path, image)

        result = READER.readtext(image_path)
        for text in result:
            if text[1].isnumeric():
                continue
            usernames_histogram[text[1].lower()] += 1

    # filter all usernames that have a levenstein distance of 3 or more to the usernames array (filtering teammates)
    for username in list(usernames_histogram):
        if (
            min(
                levenstein_distance(username, teammate_username)
                for teammate_username in teammate_usernames
            )
            <= 3
        ):
            usernames_histogram.pop(username)

    # filter all usernames that appear only once
    for username in list(usernames_histogram):
        if usernames_histogram[username] == 1:
            usernames_histogram.pop(username)

    # merge all usernames that have a levenstein distance of 1 or 2 to the usernames_histogram
    while True:
        final_usernames_histogram: Counter = Counter()
        seen = set()

        for i, username in enumerate(list(usernames_histogram)):
            if username in seen:
                continue
            shift = i + 1
            for other_username in list(usernames_histogram)[shift:]:
                if levenstein_distance(username, other_username) <= 2:
                    most_common_username = max(
                        username,
                        other_username,
                        key=lambda username: usernames_histogram[username],
                    )
                    least_common_username = min(
                        username,
                        other_username,
                        key=lambda username: usernames_histogram[username],
                    )
                    final_usernames_histogram[most_common_username] = (
                        usernames_histogram[least_common_username]
                        + usernames_histogram[most_common_username]
                    )
                    seen.add(least_common_username)
                    seen.add(most_common_username)
                    break
            else:
                final_usernames_histogram[username] = usernames_histogram[username]

        if len(final_usernames_histogram) == len(usernames_histogram):
            break

        usernames_histogram = final_usernames_histogram

    if len(final_usernames_histogram) == 0:  # pragma: no cover
        logger.warning(f"No usernames found for highlight {highlight.id}")
        return []

    queries = []
    predicted_username = max(
        final_usernames_histogram, key=final_usernames_histogram.__getitem__
    )

    for i, image in enumerate(images):
        image_path = os.path.join(highlight.images_path, image)

        result = READER.readtext(image_path)
        for text in result:
            if text[1].isnumeric():
                continue
            if levenstein_distance(text[1].lower(), predicted_username) <= 1:
                queries.append(i)
                break

    logger.debug(
        f"For highlight {highlight.id} found {predicted_username} with"
        + f"{final_usernames_histogram[predicted_username]} occurences"
    )
    return queries


def _create_league_of_legends_query_array(highlight: Highlight) -> List[int]:
    global LEAGUE_CHAMPIONS
    if not LEAGUE_CHAMPIONS:
        if not os.path.exists(LEAGUE_IMAGES_PATH):  # pragma: no cover
            logger.error("The league of legends images do not exists")
            return []

        for image_path in sorted(os.listdir(LEAGUE_IMAGES_PATH)):
            LEAGUE_CHAMPIONS.append(
                {
                    "image": cv2.imread(os.path.join(LEAGUE_IMAGES_PATH, image_path)),
                    "name": image_path.split(".")[0],
                }
            )

    images = sorted(os.listdir(highlight.images_path))
    images.sort()

    queries = []
    yellow_rgb = np.array([54, 216, 213])
    yellow_threshold = 115

    for j, image_name in enumerate(images):
        full_image_path = os.path.join(highlight.images_path, image_name)
        image = cv2.imread(full_image_path, cv2.IMREAD_COLOR)

        is_kill = False
        kill_spots = []

        regions = {
            1: image[7:51, 46:48],
            2: image[69:113, 46:48],
            3: image[132:176, 46:48],
            4: image[195:239, 46:48],
        }

        enemy_region = {
            1: image[8:49, 84:125],
            2: image[70:111, 84:125],
            3: image[133:174, 84:125],
            4: image[196:237, 84:125],
        }

        for region_index, region in regions.items():
            avg_color = np.mean(region.reshape(-1, 3), axis=0)
            color_distance = np.linalg.norm(avg_color - yellow_rgb)

            if color_distance < yellow_threshold:
                enemy_image = enemy_region[region_index]

                max_score = -1
                for champion in LEAGUE_CHAMPIONS:
                    score = cv2.matchTemplate(
                        enemy_image, champion["image"], cv2.TM_CCOEFF_NORMED
                    )
                    if score > max_score:
                        max_score = score

                if max_score > 0.75:
                    is_kill = True
                    kill_spots.append(region_index)

        if is_kill:
            queries.append(j)
    return queries


def _get_query_array(
    neural_network: Union[NeuralNetwork, None],
    highlight: Highlight,
    confidence: float,
    game: SupportedGames,
) -> List[int]:
    if neural_network:
        return _create_query_array(neural_network, highlight, confidence)
    if game == SupportedGames.THE_FINALS:
        return _create_the_finals_query_array(highlight)
    if game == SupportedGames.LEAGUE_OF_LEGENDS:
        return _create_league_of_legends_query_array(highlight)
    raise ValueError(
        f"No neural network for game {game} and no custom query array"
    )  # pragma: no cover


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
    neural_network: Union[NeuralNetwork, None],
    confidence: float,
    framerate: int,
    offset: int,
    frames_before: int,
    frames_after: int,
    game: SupportedGames = GAME,
) -> Tuple[List[Tuple[float, float]], List[Segment]]:
    """
        Extract segments from a highlight
    game
        :param highlight: highlight to extract segments from
        :param neural_network: neural network to query
        :param confidence: confidence to query
        :param offset: offset to post process
        :param framerate: framerate of the video

        :return: list of segments
    """
    queries = _get_query_array(neural_network, highlight, confidence, game)
    normalized = _normalize_queries(queries, frames_before, frames_after)
    processed = _post_process_query_array(normalized, offset, framerate)
    segments = await highlight.extract_segments(processed)

    coroutines = []
    for segment in segments:
        coroutines.append(segment.copy_video_in_lower_resolution())
    await asyncio.gather(*coroutines)

    return (processed, segments)
