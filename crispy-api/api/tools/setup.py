import asyncio
import logging
import os
import shutil
from typing import List

import ffmpeg
from PIL import Image

from api.config import SESSION, SILENCE_PATH
from api.models.filter import Filter
from api.models.highlight import Highlight
from api.models.music import Music
from api.tools.audio import video_has_audio
from api.tools.enums import SupportedGames
from api.tools.job_scheduler import JobScheduler

logger = logging.getLogger("uvicorn")


def __sanitize_path(path: str) -> str:
    for ch in (" ", "(", ")", "[", "]", "{", "}", "'", '"', ",", ".", "_"):
        path = path.replace(ch, "-")
    return path


async def handle_highlights(
    path: str,
    game: SupportedGames,
    framerate: int = 4,
    session: str = SESSION,
) -> List[Highlight]:

    if not os.path.exists(session):
        os.mkdir(session)

    highlights = Highlight.find().to_list(None)
    if len(highlights) != 0:
        index = max(highlight.index for highlight in highlights)
    else:
        index = 0

    for highlight in highlights:
        if not os.path.exists(highlight.path):
            logger.info(f"Removing highlight {highlight.path}")
            await highlight.remove()

    job_scheduler = JobScheduler(4)
    new_highlights = []
    for file in sorted(os.listdir(path)):
        file_path = os.path.join(path, file)
        if not any(highlight.path == file_path for highlight in highlights):
            logger.info(f"Adding highlight {file}")
            directory = os.path.join(
                session, __sanitize_path(os.path.splitext(file)[0])
            )

            if not os.path.exists(directory):
                os.mkdir(directory)
            highlight = Highlight(
                {
                    "path": file_path,
                    "directory": directory,
                    "index": index,
                    "enabled": True,
                }
            ).save()
            Filter({"highlight_id": highlight.id}).save()
            new_highlights.append(highlight)

            job_scheduler.schedule(
                highlight.extract_images_from_game,
                kwargs={"game": game, "framerate": framerate},
            )
            job_scheduler.schedule(highlight.extract_thumbnails)
            job_scheduler.schedule(highlight.extract_snippet_in_lower_resolution)
            index += 1

    logger.info(f"Adding {len(new_highlights)} highlights, this may take a while.")
    logger.warning("Wait for `Application startup complete.` to use Crispy.")

    job_scheduler.run_in_thread().join()

    for highlight in new_highlights:
        if not video_has_audio(highlight.path):
            tmp_path = os.path.join(highlight.directory, "tmp.mp4")

            video = ffmpeg.input(highlight.path)
            audio = ffmpeg.input(SILENCE_PATH).audio

            ffmpeg.input(highlight.path).output(
                video, audio, tmp_path, vcodec="copy", acodec="aac"
            ).overwrite_output().run()
            shutil.move(tmp_path, highlight.path)

        if Image.open(highlight.thumbnail_path_full_size).size != (1920, 1080):
            await highlight.scale_video()
            coroutines = [
                highlight.extract_thumbnails(),
                highlight.extract_snippet_in_lower_resolution(),
                highlight.extract_images_from_game(game, framerate),
            ]

            await asyncio.gather(*coroutines)

    Highlight.update_many({}, {"$set": {"job_id": None}})

    return new_highlights


async def handle_musics(path: str) -> List[Music]:
    musics = Music.find().to_list(None)
    if len(musics) != 0:
        index = max(music.index for music in musics)
    else:
        index = 0

    for music in musics:
        if not os.path.exists(music.path):
            logger.info(f"Removing music {music.path}")
            Music.delete_one(music.id)

    new_musics = []
    for file in sorted(os.listdir(path)):
        file_path = os.path.join(path, file)
        if not any(music.path == file_path for music in musics):
            music = Music({"path": file_path, "index": index, "enabled": True}).save()
            new_musics.append(music)
            index += 1

    return new_musics
