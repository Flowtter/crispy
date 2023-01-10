from typing import Any, Dict, Union

from backend.dto import Filters
from backend.json_handling import get_session_json, save_json
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from utils.constants import app


@app.get("/objects/filters/{filename}/read")
async def filters_read(filename: str) -> Union[Dict[Any, Any], HTTPException]:
    session = get_session_json()
    objects = session["objects"]

    obj = next(filter(lambda x: x["name"] == filename, objects), None)
    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    return obj["filters"]


@app.post("/objects/filters/{filename}/save")
async def filters_save(
    data: Filters, filename: str
) -> Union[Dict[Any, Any], HTTPException]:
    session = get_session_json()
    objects = session["objects"]

    obj = next(filter(lambda x: x["name"] == filename, objects), None)
    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    obj["refresh"] = True
    obj["filters"] = jsonable_encoder(data)
    session["objects"] = objects
    save_json(session)

    return obj["filters"]


@app.get("/objects/filters/{filename}/update")
async def update(filename: str) -> Union[bool, HTTPException]:
    session = get_session_json()
    objects = session["objects"]

    obj = next(filter(lambda x: x["name"] == filename, objects), None)
    if not obj:
        return HTTPException(status_code=404, detail="Object not found")
    if "refresh" in obj:
        save = obj["refresh"]
    else:
        save = False

    obj["refresh"] = False
    session["objects"] = objects
    save_json(session)

    return save


@app.get("/filters/read")
async def global_filters_read() -> Union[Dict[Any, Any], HTTPException]:
    filters = get_session_json()["filters"]
    if not filters:
        return HTTPException(status_code=404, detail="Object not found")

    return filters


@app.post("/filters/save")
async def global_filters_save(data: Filters) -> Union[Dict[Any, Any], HTTPException]:
    session = get_session_json()
    filters = session["filters"]

    if not filters:
        return HTTPException(status_code=404, detail="Object not found")

    filt = jsonable_encoder(data)
    session["filters"] = filt
    save_json(session)

    return filters
