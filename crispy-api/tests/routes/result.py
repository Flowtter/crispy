import asyncio
import os

from bson import ObjectId

from api.models.highlight import Highlight
from api.models.segment import Segment


async def test_post_results_generate_highlights(client, highlight):
    response = await client.post("/results/generate/highlights")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get(f"/results/job/{response.json()[0]}")
    assert response.status_code == 200
    assert "status" in response.json()

    while True:
        response = await client.get("/results/generate/highlights/status")
        response_data = response.json()[0]
        if response_data["status"] == "completed":
            break
        else:
            await asyncio.sleep(0.5)


async def test_post_results_generate_video(client, highlight):
    await highlight.extract_thumbnails()
    await highlight.extract_segments([[0, 1], [4, 5]])
    assert (
        Segment.find({"highlight_id": highlight.id, "enabled": True})
        .sort("start")
        .to_list(None)
    )

    response = await client.post("/results/generate/highlights")
    ids = response.json()

    while True:
        response = await client.get(f"/results/job/{ids[0]}")
        response_data = response.json()
        if response_data["status"] == "completed":
            break
        else:
            await asyncio.sleep(0.5)

    assert os.path.exists(Highlight.find_one(highlight.id).merge_path)

    response = await client.post("/results/generate/video")
    assert response.status_code == 200
    job_id = response.json()

    while True:
        response = await client.get(f"/results/job/{job_id['_id']}")
        if response.json()["status"] == "completed":
            break
        else:
            await asyncio.sleep(0.5)

    response = await client.get("/results/video")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "video/mp4"

    response = await client.get("/results/thumbnail")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/jpeg"


async def test_get_results_thumbnail(client):
    response = await client.get("/results/thumbnail")
    assert response.status_code == 404


async def test_results_get_job(client):
    response = await client.get(f"/results/job/{ObjectId()}")
    assert response.status_code == 404
