from typing import Dict, List, Optional

from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import FileResponse

from api import app
from api.models.highlight import Highlight
from api.models.music import Music
from api.tools.audio import merge_musics
from api.tools.ffmpeg import merge_videos
from api.tools.job_scheduler import JobScheduler
from api.tools.utils import get_all_jobs_from_highlights

job_scheduler = JobScheduler(4)


@app.post("/results/generate/highlights")
async def post_results_generate_highlights() -> List:
    highlights = Highlight.find({"enabled": True}).sort("index").to_list(None)
    ids = []

    for highlight in highlights:
        id = job_scheduler.schedule(highlight.concatenate_segments)
        highlight.job_id = id
        highlight.save()
        ids.append(id)

    job_scheduler.run_in_thread()
    return ids


@app.get("/results/generate/highlights/status")
async def get_results_generate_highlights_status() -> List:
    highlights = Highlight.find({"enabled": True}).to_list(None)
    return get_all_jobs_from_highlights(job_scheduler, highlights)


@app.post("/results/generate/video")
async def post_results_generate_video() -> Dict:
    musics = Music.find({"enabled": True}).sort("index").to_list(None)
    merge_musics(
        [music.path for music in musics],
        "merged.mp3",
    )

    highlights = Highlight.find({"enabled": True}).sort("index").to_list(None)

    job_id = job_scheduler.schedule(
        merge_videos,
        kwargs={
            "videos_path": [highlight.merge_path for highlight in highlights],
            "save_path": "merged.mp4",
            "delete": False,
            "audio_path": "merged.mp3",
        },
    )

    job_scheduler.run_in_thread()
    return {"_id": job_id}


@app.get("/results/job/{job_id}")
async def get_job(job_id: str) -> Optional[Dict]:
    job = job_scheduler.find_job(ObjectId(job_id))
    if job is None:
        raise HTTPException(404)
    return {
        "_id": job_id,
        "status": job["status"],
    }


@app.get("/results/video")
async def get_results_video() -> FileResponse:
    return FileResponse("merged.mp4")


@app.get("/results/thumbnail")
async def get_results_thumbnail() -> FileResponse:
    highlights = (
        Highlight.find(
            {
                "$and": [
                    {"enabled": True},
                    {"thumbnail_path": {"$exists": True}},
                ]
            }
        )
        .sort("index")
        .to_list(1)
    )

    if not highlights:
        raise HTTPException(404)

    return FileResponse(highlights[0].thumbnail_path)
