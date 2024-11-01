import asyncio
import logging
import os
from io import BytesIO
from typing import Any, Dict, List, Union

import aiohttp
import requests
from PIL import Image

from api.config import LEAGUE_IMAGES_PATH
from api.models.highlight import Highlight
from api.tools.job_scheduler import JobScheduler

logger = logging.getLogger("uvicorn")

# URL for champion data and image base
base_url = "https://ddragon.leagueoflegends.com"
version_url = f"{base_url}/realms/na.json"
json_url = f"{base_url}/cdn/VERSION/data/en_US/champion.json"
image_base_url = f"{base_url}/cdn/VERSION/img/champion"


def get_league_of_legends_version() -> Union[str, None]:
    response = requests.get(version_url)
    if response.status_code != 200:  # pragma: no cover
        logger.error("Cannot download the league of legends patch version")
        return None
    data = response.json()
    if "n" not in data or "champion" not in data["n"]:  # pragma: no cover
        logger.error("Could not extract the league of legends patch version")
    return str(data["n"]["champion"])


async def fetch_image(session: aiohttp.ClientSession, url: str, path: str) -> None:
    async with session.get(url) as response:
        if response.status != 200:  # pragma: no cover
            logger.error(f"Cannot download image from {url}")
            return
        img = Image.open(BytesIO(await response.read()))
        img.save(path)


async def download_champion_images(path: str = LEAGUE_IMAGES_PATH) -> None:
    version = get_league_of_legends_version()
    if not version:  # pragma: no cover
        logger.error("Could not download the league of legends images")
        return
    async with aiohttp.ClientSession() as session:
        champions = await session.get(json_url.replace("VERSION", version))
        if champions.status != 200:  # pragma: no cover
            logger.error("Cannot download the league of legends champion.json")
            return
        champion_names = (await champions.json())["data"].keys()

        if not os.path.exists(path):  # pragma: no cover
            os.makedirs(path)

        logger.info("Downloading league of legends champion images")
        tasks = []
        for champion in champion_names:
            image_path = os.path.join(path, f"{champion}.png")
            if os.path.exists(image_path):
                continue
            image_url = f"{image_base_url.replace('VERSION', version)}/{champion}.png"
            tasks.append(fetch_image(session, image_url, image_path))

        await asyncio.gather(*tasks)

    for champion in champion_names:
        image_path = os.path.join(path, f"{champion}.png")
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img = img.resize((41, 41), Image.ANTIALIAS)
            img.save(image_path)

    logger.info("Done downloading and resizing league champions")


def get_all_jobs_from_highlights(
    job_scheduler: JobScheduler, highlights: List[Highlight]
) -> List[Dict]:
    jobs = []
    for highlight in highlights:
        result = {
            "_id": str(highlight.id),
            "index": highlight.index,
            "status": "completed",
            "name": highlight.name,
        }
        if highlight.job_id is not None:
            job = job_scheduler.find_job(highlight.job_id)
            result["status"] = job["status"] if job is not None else "completed"
        jobs.append(result)
    return jobs


def sanitize_dict(d: Any) -> Dict:
    """Remove all keys with None, False or Empty string values from a dict/object""" ""
    return {k: v for k, v in d.items() if v}


def levenstein_distance(s1: str, s2: str) -> int:
    """Calculates the levenstein distance between two strings"""
    if len(s1) < len(s2):
        return levenstein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))

    for i, c1 in enumerate(s1):
        current_row = [i + 1]

        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))

        previous_row = current_row

    return previous_row[-1]
