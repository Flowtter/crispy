import json
import logging
import os

from PIL import Image

from api.config import DATASET_PATH, DATASET_VALUES_PATH, VIDEOS
from api.models.highlight import Highlight
from api.tools.enums import SupportedGames
from api.tools.setup import handle_highlights

logger = logging.getLogger("crispy")


def to_csv(highlight: Highlight, values: dict, dataset_path: str) -> None:
    """
    Convert all images of an highlight to a csv file

    :param highlight: Highlight to convert
    :param values: values array from dataset_values.json
    :param dataset_path: Path to the dataset folder
    """
    name = highlight.path.split("/")[-1].split(".")[0]

    inclusives_ranges = []
    if name not in values:
        logger.warning(f"{name} not in values, using []")
    else:
        inclusives_ranges = values[name]

    dict_values = []

    for inclusive_range in inclusives_ranges:
        if not inclusive_range:
            continue

        if len(inclusive_range) == 1:
            inclusive_range.append(inclusive_range[0])

        for i in range(inclusive_range[0], inclusive_range[1] + 1):
            dict_values.append(i)

    csv = []
    images = sorted(os.listdir(highlight.images_path))

    for i, image in enumerate(images):
        im = Image.open(os.path.join(highlight.images_path, image))

        pixel_values = list(im.getchannel("R").getdata())
        pixel_values.insert(0, int(i in dict_values))

        csv.append(pixel_values)

    with open(os.path.join(dataset_path, name + ".csv"), "w") as f:
        for row in csv:
            f.write(",".join([str(x) for x in row]) + "\n")


def concat_csv(dataset_path: str) -> None:
    """
    Merge all the csv files into one result.csv

    :param dataset_path: Path to the dataset folder
    """
    result = []
    for file in sorted(os.listdir(dataset_path)):
        if os.path.splitext(file)[1] == ".csv":
            if file in ("result.csv", "test.csv"):
                continue
            with open(os.path.join(dataset_path, file), "r") as f:
                lines = f.readlines()
                result.extend(lines)

    with open(os.path.join(dataset_path, "result.csv"), "w") as f:
        f.writelines(result)


async def create_dataset(
    game: SupportedGames,
    video_path: str = VIDEOS,
    framerate: int = 8,
    dataset_path: str = DATASET_PATH,
    dataset_values_path: str = DATASET_VALUES_PATH,
) -> None:
    """
    Create a dataset from the highlights

    :param game: Game to create the dataset from
    """
    await handle_highlights(video_path, game, framerate, dataset_path)

    if not os.path.exists(dataset_values_path):
        raise ValueError(
            f"Values for the dataset does not exist, should be in {dataset_values_path}"
        )

    with open(dataset_values_path, "r") as f:
        values = json.load(f)

    highlights = await Highlight.find({}).to_list(None)

    for highlight in highlights:
        logger.info(f"Doing: {highlight.path}")
        to_csv(highlight, values, dataset_path)
    concat_csv(dataset_path)
