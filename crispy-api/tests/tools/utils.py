import os
import shutil
import time

from PIL import Image

from api.tools.utils import download_champion_images, levenstein_distance


async def test_levenshtein_distance():
    assert levenstein_distance("", "") == 0
    assert levenstein_distance("test", "test") == 0

    assert levenstein_distance("test", "tst") == 1
    assert levenstein_distance("test", "tast") == 1
    assert levenstein_distance("test", "teest") == 1

    assert levenstein_distance("test", "yolo") == 4

    assert levenstein_distance("test", "y") == 4
    assert levenstein_distance("y", "test") == 4
    assert levenstein_distance("test", "t") == 3
    assert levenstein_distance("t", "test") == 3
    assert levenstein_distance("test", "") == 4
    assert levenstein_distance("", "test") == 4


async def test_download_champion_images(tmp_path):
    start_time = time.time()
    await download_champion_images(tmp_path)
    first_download_time = time.time() - start_time

    assert os.path.exists(tmp_path)
    assert len(os.listdir(tmp_path)) > 100
    image_path = os.path.join(tmp_path, os.listdir(tmp_path)[0])

    with Image.open(image_path) as image:
        assert image.size == (41, 41)

    start_time = time.time()
    await download_champion_images(tmp_path)
    second_download_time = time.time() - start_time

    assert second_download_time < first_download_time

    shutil.rmtree(tmp_path)
