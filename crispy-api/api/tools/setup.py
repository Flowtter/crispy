import logging
import os
import shutil
from collections import Counter
from typing import List

import ffmpeg
from PIL import Image

from api.config import READER, SESSION, SILENCE_PATH, STRETCH
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


def handle_the_finals(
    new_highlights: List[Highlight],
    framerate: int = 4,
) -> None:
    for highlight in new_highlights:
        path = os.path.join(highlight.directory, "usernames")
        images = os.listdir(path)
        usernames: List[str] = ["", ""]
        usernames_histogram: Counter = Counter()

        for i in range(0, len(images), framerate):
            image = images[i]
            image_path = os.path.join(path, image)
            result = READER.readtext(image_path)
            for text in result:
                if text[1].isnumeric():
                    continue
                usernames_histogram[text[1]] += 1
            most_common_usernames = usernames_histogram.most_common(2)
            if most_common_usernames[0][1] >= 10 and most_common_usernames[1][1] >= 10:
                usernames = [most_common_usernames[0][0], most_common_usernames[1][0]]
                break
        highlight.update({"usernames": usernames})
        highlight.save()


def handle_specific_game(
    new_highlights: List[Highlight],
    game: SupportedGames,
    framerate: int = 4,
) -> None:
    if game == SupportedGames.THEFINALS:
        handle_the_finals(new_highlights, framerate)


async def handle_highlights(
    path: str,
    game: SupportedGames,
    framerate: int = 4,
    session: str = SESSION,
    stretch: bool = STRETCH,
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
            await highlight.extract_thumbnails()

            index += 1

    logger.info(f"Adding {len(new_highlights)} highlights, this may take a while.")
    logger.warning("Wait for `Application startup complete.` to use Crispy.")

    target_size = (1440, 1080) if stretch else (1920, 1080)
    for highlight in new_highlights:
        if not video_has_audio(highlight.path):
            tmp_path = os.path.join(highlight.directory, "tmp.mp4")

            video = ffmpeg.input(highlight.path)
            audio = ffmpeg.input(SILENCE_PATH).audio

            ffmpeg.input(highlight.path).output(
                video, audio, tmp_path, vcodec="copy", acodec="aac"
            ).overwrite_output().run(quiet=True)
            shutil.move(tmp_path, highlight.path)

        if Image.open(highlight.thumbnail_path_full_size).size != target_size:
            await highlight.scale_video(*target_size, stretch=stretch)
            await highlight.extract_thumbnails()

    job_scheduler = JobScheduler(4)
    for highlight in new_highlights:
        job_scheduler.schedule(
            highlight.extract_images_from_game,
            kwargs={"game": game, "framerate": framerate, "stretch": stretch},
        )
        job_scheduler.schedule(
            highlight.extract_snippet_in_lower_resolution, kwargs={"stretch": stretch}
        )

    job_scheduler.run_in_thread().join()

    Highlight.update_many({}, {"$set": {"job_id": None}})

    handle_specific_game(new_highlights, game, framerate)

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
