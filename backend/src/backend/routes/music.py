import os
from typing import Any, Dict, List, Union

from backend.dto import Reorder
from backend.json_handling import get_session_json, save_json
from fastapi import HTTPException
from fastapi.responses import FileResponse
from utils.constants import MUSICS_PATH, TMP_PATH, app


@app.get("/musics/{filename}")
async def get_music(filename: str) -> FileResponse:
    return FileResponse(os.path.join(MUSICS_PATH, filename + ".mp3"))


@app.get("/musics/{filename}/info")
async def info_music(filename: str) -> Union[bool, HTTPException]:
    session = get_session_json()
    musics = session["musics"]

    music = next(filter(lambda x: x["name"] == filename, musics), None)

    if not music:
        return HTTPException(status_code=404, detail="Music not found")

    return music["enabled"]


@app.get("/musics/{filename}/switch")
async def switch_music(filename: str) -> Union[Dict[Any, Any], HTTPException]:
    session = get_session_json()
    musics = session["musics"]

    music = next(filter(lambda x: x["name"] == filename, musics), None)

    if not music:
        return HTTPException(status_code=404, detail="Music not found")

    index = musics.index(music)

    music["enabled"] = not music["enabled"]
    musics[index] = music

    session["musics"] = musics

    save_json(session)

    with open(os.path.join(TMP_PATH, "recompile.json"), "w") as f:
        f.write('{"switch":true}')

    with open(os.path.join(TMP_PATH, "music.json"), "w") as f:
        f.write('{"switch":true}')

    return music["enabled"]


@app.post("/musics/reorder")
async def music_reorder(data: List[Reorder]) -> Dict[Any, Any]:
    session = get_session_json()
    musics = session["musics"]

    new_musics = []
    for datum in data:
        music = next(filter(lambda x: x["name"] == datum.name, musics), None)
        new_musics.append(music)

    session["musics"] = new_musics

    with open(os.path.join(TMP_PATH, "recompile.json"), "w") as f:
        f.write('{"reorder":true}')

    with open(os.path.join(TMP_PATH, "music.json"), "w") as f:
        f.write('{"reorder":true}')

    save_json(session)
    return session
