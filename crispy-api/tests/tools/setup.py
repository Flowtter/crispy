import os
import shutil

from api.models.highlight import Highlight
from api.models.music import Music
from api.tools.enums import SupportedGames
from api.tools.setup import handle_highlights, handle_musics
from tests.constants import MAIN_MUSIC, MAIN_VIDEO, MAIN_VIDEO_NO_AUDIO


async def test_handle_highlights(tmp_path):
    tmp_session = os.path.join(tmp_path, "session")
    tmp_resources = os.path.join(tmp_path, "resources")
    os.mkdir(tmp_resources)

    assert not await handle_highlights(
        tmp_resources, SupportedGames.VALORANT, session=tmp_session
    )
    shutil.copy(MAIN_VIDEO, tmp_resources)

    assert await handle_highlights(
        tmp_resources, SupportedGames.VALORANT, session=tmp_session
    )
    assert not await handle_highlights(
        tmp_resources, SupportedGames.VALORANT, session=tmp_session
    )

    shutil.copy(MAIN_VIDEO_NO_AUDIO, tmp_resources)
    assert await handle_highlights(
        tmp_resources, SupportedGames.VALORANT, session=tmp_session
    )

    assert Highlight.count_documents() == 2

    os.remove(os.path.join(tmp_resources, "main-video.mp4"))

    assert not await handle_highlights(
        tmp_resources, SupportedGames.VALORANT, session=tmp_session
    )

    assert len(Highlight.find().to_list(None)) == 1

    os.remove(os.path.join(tmp_resources, "main-video-no-audio.mp4"))
    shutil.copy(MAIN_VIDEO, tmp_resources)

    new_highlights = await handle_highlights(
        tmp_resources, SupportedGames.VALORANT, session=tmp_session
    )

    highlights = Highlight.find().to_list(None)

    assert len(highlights) == 1
    assert len(new_highlights) == 1

    assert highlights[0].id == new_highlights[0].id

    shutil.rmtree(tmp_resources)


async def test_handle_musics(tmp_path):
    tmp_resources = os.path.join(tmp_path, "resources")
    os.mkdir(tmp_resources)

    assert not await handle_musics(tmp_resources)

    shutil.copy(MAIN_MUSIC, tmp_resources)

    assert await handle_musics(tmp_resources)
    assert not await handle_musics(tmp_resources)

    musics = Music.find().to_list(None)
    assert len(musics) == 1
    assert musics[0].view().get("name") == "trumpet"

    os.remove(os.path.join(tmp_resources, "trumpet.mp3"))

    assert not await handle_musics(tmp_resources)

    assert len(Music.find().to_list(None)) == 0

    shutil.rmtree(tmp_resources)
