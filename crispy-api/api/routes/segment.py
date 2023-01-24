from typing import Dict, Union

from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import FileResponse

from api import app
from api.models.segment import Segment


@app.get("/segments/{segment_id}")
async def get_segments_id(segment_id: str) -> Union[Dict, HTTPException]:
    segment = Segment.find_one(ObjectId(segment_id))
    if segment is None:
        raise HTTPException(404)
    return segment.view()


@app.get("/segments/{segment_id}/video")
async def get_segments_id_video(segment_id: str) -> FileResponse:
    segment = Segment.find_one(ObjectId(segment_id))
    if segment is None:
        raise HTTPException(404)
    return FileResponse(segment.downscaled_path or segment.path)


@app.post("/segments/{segment_id}/switch-status")
async def post_segments_id_switch_status(segment_id: str) -> None:
    segment = Segment.find_one(ObjectId(segment_id))
    if segment is None:
        raise HTTPException(404)
    segment.enabled = not segment.enabled
    segment.save()
