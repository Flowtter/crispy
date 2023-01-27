from typing import Any, Dict, Union

from bson import ObjectId
from fastapi import HTTPException
from pydantic import BaseModel

from api import app
from api.models.filter import Filter


@app.get("/filters/{highlight_id}")
async def get_filters_highlight_id(
    highlight_id: str,
) -> Union[Dict[Any, Any], HTTPException]:
    if highlight_id == "global":
        _filter = Filter.find_one({"global": True})
    else:
        _filter = Filter.find_one({"highlight_id": ObjectId(highlight_id)})
    if not _filter:
        if highlight_id == "global":
            _filter = Filter({"global": True}).save()
        else:
            raise HTTPException(404)
    return _filter.view()


class NoProp(BaseModel):
    """DTO for no value filter"""

    box: bool


class Single(BaseModel):
    """DTO for single value filter"""

    box: bool
    value: Union[float, None]


class Filters(BaseModel):
    """DTO for filters"""

    blur: Single
    hflip: NoProp
    vflip: NoProp
    saturation: Single
    brightness: Single
    zoom: Single
    grayscale: NoProp


@app.post("/filters/{highlight_id}")
async def post_filters_highlight_id(
    highlight_id: str, filters: Filters
) -> Union[Dict[Any, Any], HTTPException]:
    if highlight_id == "global":
        _filter = Filter.find_one({"global": True})
    else:
        _filter = Filter.find_one({"highlight_id": ObjectId(highlight_id)})

    if not _filter:
        raise HTTPException(404)

    filter_dict = filters.dict()
    result = {}

    for key, value in filter_dict.items():
        if "value" in value and value["box"]:
            result[key] = value["value"]
        else:
            result[key] = value["box"]

    _filter.update({"filters": result})

    if "updating" in _filter.view():
        _filter.update({"updating": False})

    _filter.save()
    return _filter.view()


@app.post("/filters/{highlight_id}/update")
async def post_filters_highlight_id_update(
    highlight_id: str,
) -> Union[Dict[Any, Any], HTTPException]:
    if highlight_id == "global":
        raise HTTPException(403)
    else:
        _filter = Filter.find_one({"highlight_id": ObjectId(highlight_id)})

    if not _filter:
        raise HTTPException(404)

    _filter.update({"updating": True})
    _filter.save()
    return _filter.view()
