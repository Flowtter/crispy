import asyncio
import csv
import logging
import os
import sys

import ffmpeg
import pytest
from httpx import AsyncClient
from mongo_thingy import Thingy
from mutagen.mp3 import MP3
from PIL import Image

from api import app, init_database
from api.models.filter import Filter
from api.models.highlight import Highlight
from api.models.music import Music
from api.models.segment import Segment
from api.tools.AI.network import NeuralNetwork
from api.tools.enums import SupportedGames
from api.tools.image import compare_image
from api.tools.job_scheduler import JobScheduler
from api.tools.utils import download_champion_images
from tests.constants import MAIN_MUSIC, MAIN_VIDEO, ROOT_ASSETS, VALORANT_NETWORK


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="https://tests") as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
def database():
    init_database(".tests-data")

    database = Thingy.database
    assert "test" in database.name
    return database


@pytest.fixture(autouse=True)
def clean_database(database):
    for collection_name in database.list_collection_names():
        collection = database[collection_name]
        collection.delete_many({})


@pytest.fixture
async def highlight(tmp_path):
    return Highlight(
        {
            "path": MAIN_VIDEO,
            "directory": str(tmp_path),
            "thumbnail_path": None,
            "images_path": None,
            "videos_path": None,
            "index": 1,
            "enabled": True,
        }
    ).save()


@pytest.fixture
async def highlight_overwatch(highlight):
    highlight.path = os.path.join("tests", "assets", "main-video-overwatch.mp4")
    return highlight.save()


@pytest.fixture
async def segment(highlight):
    return Segment(
        {
            "highlight_id": highlight.id,
            "path": MAIN_VIDEO,
            "start": 0.0,
            "end": 1.0,
            "enabled": True,
        }
    ).save()


@pytest.fixture
async def filter_h(highlight):
    return Filter({"highlight_id": highlight.id}).save()


@pytest.fixture
async def music():
    return Music(
        {
            "path": MAIN_MUSIC,
            "enabled": True,
            "index": 1,
        }
    ).save()


@pytest.fixture
async def job_scheduler():
    return JobScheduler()


@pytest.fixture
async def neural_network():
    neural_network = NeuralNetwork(SupportedGames.VALORANT, 0.01)
    neural_network.load(VALORANT_NETWORK)
    return neural_network


@pytest.fixture(autouse=True)
async def compare_folder(request, tmp_path):
    yield
    CompareFolder(request, tmp_path)


class CompareFolder:
    """
    Compare a folder with the expected one

    it should compare the number of files and the content of each file
    """

    def __init__(self, request, tmp_path):
        root_expected = os.path.join(ROOT_ASSETS, "compare", request.node.name)

        if not os.path.exists(root_expected):
            if os.path.exists(tmp_path) and os.listdir(tmp_path):
                assert (
                    False
                ), "The tmp_path is not empty but the expected folder does not exist"
            return

        root = str(tmp_path)

        self.chunk_size = 2**16
        self.extract_all_videos(root)
        self.is_same_directory(root, root_expected)

    def extract_frames(self, video_path, framerate=8):
        image_path = os.path.splitext(video_path)[0]
        (
            ffmpeg.input(video_path)
            .filter("fps", fps=f"1/{round(1 / framerate, 5)}")
            .output(image_path + "-%8d.jpg", start_number=0)
            .run(quiet=True)
        )

    def is_same_files(self, file_path, expected_file_path):
        assert os.path.getsize(file_path) == os.path.getsize(expected_file_path)
        with open(expected_file_path, "rb") as e:
            with open(file_path, "rb") as f:
                chunk = expected_chunk = True
                while chunk and expected_chunk:
                    chunk = f.read(self.chunk_size)
                    expected_chunk = e.read(self.chunk_size)
                    assert chunk == expected_chunk
                assert not (chunk or expected_chunk)

    def is_same_audio(self, file_path, expected_file_path):
        audio = MP3(file_path)
        expected_audio = MP3(expected_file_path)

        assert abs(audio.info.length - expected_audio.info.length) < 0.1

    def is_same_csv(self, file_path, expected_file_path):
        with open(expected_file_path, "r") as e:
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                expected_reader = csv.reader(e)
                assert len(list(reader)) == len(list(expected_reader))

                for line, expected_line in zip(reader, expected_reader):
                    assert len(line) == len(expected_line)
                    assert line[0] == expected_line[0]

    def is_same_directory(self, folder, expected_folder):
        assert os.path.exists(expected_folder)
        assert os.path.exists(folder)

        expected_files = os.listdir(expected_folder)
        files = os.listdir(folder)

        assert len(files) == len(expected_files)

        for file in files:
            expected_file_path = os.path.join(expected_folder, file)
            file_path = os.path.join(folder, file)

            assert os.path.exists(expected_file_path)
            assert os.path.exists(file_path)

            assert os.path.basename(file_path) == os.path.basename(expected_file_path)
            assert os.path.isdir(file_path) == os.path.isdir(expected_file_path)

            extension = os.path.splitext(file_path)[1]

            if os.path.isdir(file_path):
                self.is_same_directory(file_path, expected_file_path)
            elif extension in (".jpg", ".png", ".bmp"):
                assert Image.open(file_path).size == Image.open(expected_file_path).size
                assert compare_image(file_path, expected_file_path)
            elif extension == ".mp3":
                self.is_same_audio(file_path, expected_file_path)
            elif extension == ".csv":
                self.is_same_csv(file_path, expected_file_path)
            else:
                self.is_same_files(file_path, expected_file_path)

    def extract_all_videos(self, folder):
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isdir(file_path):
                self.extract_all_videos(file_path)
            elif os.path.splitext(file_path)[1] == ".mp4":
                self.extract_frames(file_path)
                os.remove(file_path)


def pytest_sessionstart(session):
    if not (os.path.exists(ROOT_ASSETS) and os.listdir(ROOT_ASSETS)):
        print(
            "Directory tests/assets does not exists. Create it using `git submodule update --init`"
        )
        sys.exit(1)
    asyncio.run(download_champion_images())
    logging.getLogger("uvicorn").disabled = True
