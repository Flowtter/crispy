from typing import Any, Dict, List, Union

from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from api import app
from api.models.music import Music


@app.get("/musics")
async def get_musics() -> List:
    musics = Music.find().sort("index").to_list(None)
    return [music.view() for music in musics]


@app.get("/musics/{music_id}")
async def get_musics_id(music_id: str) -> Union[Dict[str, Any], HTTPException]:
    music = Music.find_one(ObjectId(music_id))
    if music is None:
        raise HTTPException(404)
    return music.view()


@app.get("/musics/{music_id}/music")
async def get_musics_id_music(music_id: str) -> FileResponse:
    music = Music.find_one(ObjectId(music_id))
    if music is None:
        raise HTTPException(404)
    return FileResponse(music.path)


@app.post("/musics/{music_id}/switch-status")
async def post_musics_id_switch_status(music_id: str) -> None:
    music = Music.find_one(ObjectId(music_id))
    if music is None:
        raise HTTPException(404)
    music.enabled = not music.enabled
    music.save()


class Reorder(BaseModel):
    music_id: str
    other_music_id: str


@app.post("/musics/reorder")
async def post_musics_id_move_other_music_id(reorder: Reorder) -> None:
    if reorder.music_id == reorder.other_music_id:
        raise HTTPException(400)

    music = Music.find_one(ObjectId(reorder.music_id))
    other_music = Music.find_one(ObjectId(reorder.other_music_id))
    if music is None or other_music is None:
        raise HTTPException(404)

    music.index, other_music.index = other_music.index, music.index
    music.save()
    other_music.save()
