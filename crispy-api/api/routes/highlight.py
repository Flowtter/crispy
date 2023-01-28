from typing import Dict, List, Union

from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from api import app, neural_network
from api.models.highlight import Highlight
from api.models.segment import Segment
from api.tools.job_scheduler import JobScheduler
from api.tools.utils import get_all_jobs_from_highlights
from api.tools.video import extract_segments
from api.config import FRAMERATE, OFFSET, FRAMES_BEFORE, FRAMES_AFTER, CONFIDENCE

job_scheduler = JobScheduler(4)


@app.get("/highlights")
async def get_highlights() -> List:
    highlights = Highlight.find().sort("index").to_list(None)
    return [highlight.view() for highlight in highlights]


@app.get("/highlights/{highlight_id}")
async def get_highlights_id(highlight_id: str) -> Union[Dict, HTTPException]:
    highlight = Highlight.find_one(ObjectId(highlight_id))
    if highlight is None:
        raise HTTPException(404)
    return highlight.view()


@app.get("/highlights/{highlight_id}/snippet")
async def get_highlights_id_snippet(highlight_id: str) -> FileResponse:
    highlight = Highlight.find_one(ObjectId(highlight_id))
    if highlight is None:
        raise HTTPException(404)
    return FileResponse(highlight.snippet_path)


@app.get("/highlights/{highlight_id}/thumbnail")
async def get_highlights_id_thumbnail(highlight_id: str) -> FileResponse:
    highlight = Highlight.find_one(ObjectId(highlight_id))
    if highlight is None:
        raise HTTPException(404)
    return FileResponse(highlight.thumbnail_path)


class Reorder(BaseModel):
    highlight_id: str
    other_highlight_id: str


@app.post("/highlights/reorder")
async def post_highlights_id_move_other_highlight_id(reorder: Reorder) -> None:
    if reorder.highlight_id == reorder.other_highlight_id:
        raise HTTPException(400)

    highlight = Highlight.find_one(ObjectId(reorder.highlight_id))
    other_highlight = Highlight.find_one(ObjectId(reorder.other_highlight_id))
    if highlight is None or other_highlight is None:
        raise HTTPException(404)

    highlight.index, other_highlight.index = other_highlight.index, highlight.index
    highlight.save()
    other_highlight.save()


@app.post("/highlights/{highlight_id}/switch-status")
async def post_highlights_id_switch_status(highlight_id: str) -> None:
    highlight = Highlight.find_one(ObjectId(highlight_id))
    if highlight is None:
        raise HTTPException(404)
    highlight.enabled = not highlight.enabled
    highlight.save()


@app.post("/highlights/segments/generate")
async def post_highlights_segments_generate() -> None:
    highlights = Highlight.find({"enabled": True}).to_list(None)

    for highlight in highlights:
        highlight.job_id = job_scheduler.schedule(
            extract_segments,
            kwargs={
                "highlight": highlight,
                "neural_network": neural_network,
                "confidence": CONFIDENCE,
                "framerate": FRAMERATE,
                "offset": OFFSET,
                "frames_before": FRAMES_BEFORE,
                "frames_after": FRAMES_AFTER,
            },
        )
        highlight.save()
    job_scheduler.run_in_thread()


@app.get("/highlights/segments/generate/status")
async def get_highlights_segments_generate_status() -> List[Dict]:
    highlights = Highlight.find({"enabled": True}).to_list(None)
    return get_all_jobs_from_highlights(job_scheduler, highlights)


@app.get("/highlights/{highlight_id}/segments/status")
async def get_highlights_id_segments_status(highlight_id: str) -> Dict:
    highlight = Highlight.find_one(ObjectId(highlight_id))
    if highlight is None:
        raise HTTPException(404)

    if highlight.enabled is False:
        return {"status": "disabled"}

    job = job_scheduler.find_job(highlight.job_id)

    if job is None:
        raise HTTPException(404)

    return {"status": job["status"]}


@app.get("/highlights/{highlight_id}/segments")
async def get_highlights_id_segments(highlight_id: str) -> List:
    segments = (
        Segment.find({"highlight_id": ObjectId(highlight_id)})
        .sort("start", 1)
        .to_list(None)
    )
    return [segment.view() for segment in segments]
