import logging
import os
from typing import List

from api.config import SESSION
from api.models.highlight import Highlight
from api.models.music import Music
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
            new_highlights.append(highlight)

            job_scheduler.schedule(
                highlight.extract_images_from_game,
                kwargs={"game": game, "framerate": framerate},
            )
            job_scheduler.schedule(highlight.extract_thumbnail)
            job_scheduler.schedule(highlight.extract_snippet_in_lower_resolution)
            index += 1

    logger.info(f"Adding {len(new_highlights)} highlights, this may take a while.")
    logger.info("Wait for `Application startup complete.` to use Crispy.")

    job_scheduler.run_in_thread().join()

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
