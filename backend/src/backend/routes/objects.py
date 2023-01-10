import os
from typing import Any, Dict, List, Union

from backend.dto import Reorder
from backend.json_handling import get_session_json, save_json
from fastapi import HTTPException
from fastapi.responses import FileResponse
from utils.constants import CUT, FRONTEND_PATH, IMAGES_PATH, TMP_PATH, app
from utils.IO import io


@app.post("/objects/reorder")
async def reorder(data: List[Reorder]) -> Dict[Any, Any]:
    session = get_session_json()
    objects = session["objects"]
    new_objects = []
    for datum in data:
        obj = next(filter(lambda x: x["name"] == datum.name, objects), None)
        new_objects.append(obj)
    session["objects"] = new_objects

    with open(os.path.join(TMP_PATH, "recompile.json"), "w") as f:
        f.write('{"reorder":true}')

    save_json(session)
    return session


@app.get("/objects/{filename}/image")
async def get_image(filename: str) -> FileResponse:
    return FileResponse(os.path.join(IMAGES_PATH, filename + ".jpg"))


@app.get("/objects/{filename}/video")
def get_video(filename: str) -> FileResponse:
    return FileResponse(os.path.join(FRONTEND_PATH, filename + ".mp4"))


# The next four functions could use a query parameter
# To avoid code duplication
@app.get("/objects/{filename}/info")
async def get_object_info(filename: str) -> Union[Dict[Any, Any], HTTPException]:
    session = get_session_json()
    objects = session["objects"]

    obj = next(filter(lambda x: x["name"] == filename, objects), None)
    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    return obj


@app.get("/objects/{filename}/{cut}/info")
async def get_cut_info(filename: str, cut: str) -> Union[Dict[Any, Any], HTTPException]:
    session = get_session_json()
    objects = session["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)

    if not obj:
        return HTTPException(status_code=404, detail="Object not found")
    result = next(filter(lambda x: x[0] == cut, obj["cuts"]), None)

    if not result:
        return HTTPException(status_code=404, detail="Cut not found")

    return {"enabled": result[1]}


@app.get("/objects/{filename}/switch")
async def switch(filename: str) -> Union[Dict[Any, Any], HTTPException]:
    session = get_session_json()
    objects = session["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)

    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    index = objects.index(obj)

    obj["enabled"] = not obj["enabled"]
    objects[index] = obj

    session["objects"] = objects

    save_json(session)

    with open(os.path.join(TMP_PATH, "recompile.json"), "w") as f:
        f.write('{"switch":true}')

    return obj["enabled"]


@app.get("/objects/{filename}/{cut}/switch")
async def switch_cut(filename: str, cut: str) -> Union[Dict[Any, Any], HTTPException]:
    session = get_session_json()
    objects = session["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)

    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    found_cut = next(filter(lambda x: x[0] == cut, obj["cuts"]), None)

    if not found_cut:
        return HTTPException(status_code=404, detail="Cut not found")

    index = objects.index(obj)
    objects[index] = obj

    c = obj["cuts"].index(found_cut)
    obj["cuts"][c] = (obj["cuts"][c][0], not obj["cuts"][c][1])
    objects[index] = obj

    session["objects"] = objects

    save_json(session)

    with open(os.path.join(TMP_PATH, "recompile.json"), "w") as f:
        f.write('{"switch":true}')

    return obj["enabled"]


@app.get("/objects/{filename}/{cut}")
def get_cut(filename: str, cut: str) -> FileResponse:
    return FileResponse(
        os.path.join(TMP_PATH, io.generate_clean_name(filename), CUT, cut + ".mp4")
    )
