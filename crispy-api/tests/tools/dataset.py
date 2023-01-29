import os
import shutil

import pytest

from api.tools.dataset import create_dataset
from api.tools.enums import SupportedGames
from tests.constants import DATASET_VALUES_PATH, VIDEOS_PATH


async def test_create_dataset(tmp_path):
    tmp_videos = os.path.join(tmp_path, "tmp_videos")
    os.mkdir(tmp_videos)
    for file in os.listdir(VIDEOS_PATH):
        shutil.copy(os.path.join(VIDEOS_PATH, file), tmp_videos)

    await create_dataset(
        SupportedGames.VALORANT, tmp_videos, 8, tmp_path, DATASET_VALUES_PATH
    )

    await create_dataset(
        SupportedGames.VALORANT, tmp_videos, 8, tmp_path, DATASET_VALUES_PATH
    )

    with pytest.raises(ValueError):
        await create_dataset(
            SupportedGames.VALORANT, tmp_videos, 8, tmp_path, "not_a_path"
        )

    for file_or_folder in os.listdir(tmp_path):
        if file_or_folder == "result.csv":
            continue
        else:
            path = os.path.join(tmp_path, file_or_folder)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
