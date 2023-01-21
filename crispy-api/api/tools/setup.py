import asyncio
import logging
import os
from typing import List

from api.config import SESSION
from api.models.highlight import Highlight
from api.tools.enums import SupportedGames

logger = logging.getLogger("crispy")


async def handle_highlights(
    path: str,
    game: SupportedGames,
    framerate: int = 4,
    session: str = SESSION,
) -> List[Highlight]:

    if not os.path.exists(session):
        os.mkdir(session)

    highlights = Highlight.find().to_list(None)
    for highlight in highlights:
        if not os.path.exists(highlight.path):
            logger.info(f"Removing highlight {highlight.path}")
            await highlight.remove()

    new_highlights = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if not any(highlight.path == file_path for highlight in highlights):
            logger.info(f"Adding highlight {file}")
            directory = os.path.join(session, file.split(".")[0])
            if not os.path.exists(directory):
                os.mkdir(directory)
            highlight = Highlight(
                {
                    "path": file_path,
                    "directory": directory,
                }
            ).save()
            new_highlights.append(highlight)
            images_coroutine = highlight.extract_images_from_game(game, framerate)
            keyframes_coroutine = highlight.extract_keyframes()

            await asyncio.gather(images_coroutine, keyframes_coroutine)

    return new_highlights
