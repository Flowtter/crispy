import os
import shutil

from bson import ObjectId

from api.models.highlight import Highlight


async def test_get_highlights(client, highlight):
    response = await client.get("/highlights")
    highlight_view = highlight.view()
    highlight_view["_id"] = str(highlight.id)

    assert response.status_code == 200
    assert response.json() == [highlight_view]

    other_highlight = Highlight(
        {
            "index": 0,
            "path": "path",
        }
    ).save()
    other_highlight_view = other_highlight.view()
    other_highlight_view["_id"] = str(other_highlight.id)

    response = await client.get("/highlights")
    assert response.status_code == 200
    assert response.json() == [other_highlight_view, highlight_view]


async def test_get_highlights_id(client, highlight):
    highlight_view = highlight.view()
    highlight_view["_id"] = str(highlight.id)

    response = await client.get(f"/highlights/{highlight.id}")
    assert response.status_code == 200
    assert response.json() == highlight_view

    response = await client.get(f"/highlights/{ObjectId()}")
    assert response.status_code == 404


async def test_get_highlights_id_snippet(client, highlight):
    await highlight.extract_snippet_in_lower_resolution()

    response = await client.get(f"/highlights/{highlight.id}/snippet")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "video/mp4"
    assert response.headers["Content-Length"] != "0"

    response = await client.get(f"/highlights/{ObjectId()}/snippet")
    assert response.status_code == 404

    os.remove(highlight.snippet_path)


async def test_get_highlights_id_thumbnail(client, highlight):
    await highlight.extract_thumbnail()

    response = await client.get(f"/highlights/{highlight.id}/thumbnail")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/jpeg"
    assert response.headers["Content-Length"] != "0"

    response = await client.get(f"/highlights/{ObjectId()}/thumbnail")
    assert response.status_code == 404

    os.remove(highlight.thumbnail_path)


async def test_post_highlights_id_move_other_highlight_id(client, highlight):
    other_highlight = Highlight(
        {
            "index": 0,
            "path": "path",
        }
    ).save()

    response = await client.post(
        "/highlights/reorder",
        json={
            "highlight_id": str(highlight.id),
            "other_highlight_id": str(highlight.id),
        },
    )
    assert response.status_code == 400

    response = await client.post(
        "/highlights/reorder",
        json={
            "highlight_id": str(highlight.id),
            "other_highlight_id": str(other_highlight.id),
        },
    )
    assert response.status_code == 200

    assert Highlight.find_one(highlight.id).index == 0
    assert Highlight.find_one(other_highlight.id).index == 1

    response = await client.post(
        "/highlights/reorder",
        json={
            "highlight_id": str(highlight.id),
            "other_highlight_id": str(ObjectId()),
        },
    )
    assert response.status_code == 404

    response = await client.post(
        "/highlights/reorder",
        json={
            "highlight_id": str(ObjectId()),
            "other_highlight_id": str(other_highlight.id),
        },
    )
    assert response.status_code == 404


async def test_post_highlights_id_switch_status(client, highlight):
    response = await client.post(f"/highlights/{highlight.id}/switch-status")
    assert response.status_code == 200
    assert Highlight.find_one(highlight.id).enabled is False

    response = await client.post(f"/highlights/{highlight.id}/switch-status")
    assert response.status_code == 200
    assert Highlight.find_one(highlight.id).enabled is True

    response = await client.post(f"/highlights/{ObjectId()}/switch-status")
    assert response.status_code == 404


async def test_post_highlights_segments_generate(client):
    Highlight({"enabled": False}).save()

    response = await client.post("/highlights/segments/generate")
    assert response.status_code == 200

    response = await client.get("/highlights/segments/generate/status")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_highlights_segments_generate_status_no_jobs(client, highlight):
    response = await client.get("/highlights/segments/generate/status")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    for key in ["_id", "status", "index", "name"]:
        assert key in response_data[0]


async def test_get_highlights_segments_generate_status_jobs(client, highlight):
    response = await client.post("/highlights/segments/generate")
    assert response.status_code == 200

    response = await client.get("/highlights/segments/generate/status")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    for key in ["_id", "status", "index", "name"]:
        assert key in response_data[0]


async def test_post_highlights_id_segments_status(client, highlight):
    response = await client.get(f"/highlights/{highlight.id}/segments/status")
    assert response.status_code == 404

    response = await client.get(f"/highlights/{ObjectId()}/segments/status")
    assert response.status_code == 404

    await client.post("/highlights/segments/generate")

    response = await client.get(f"/highlights/{highlight.id}/segments/status")
    assert response.status_code == 200
    assert "status" in response.json()

    other_highlight = Highlight({"enabled": False}).save()
    response = await client.get(f"/highlights/{other_highlight.id}/segments/status")
    assert response.status_code == 200
    assert response.json()["status"] == "disabled"


async def test_get_highlights_id_segments(client, highlight):
    assert highlight.segments_path is None
    await highlight.extract_segments([[0, 1], [2, 3]])
    assert highlight.segments_path is not None

    response = await client.get(f"/highlights/{highlight.id}/segments")
    assert response.status_code == 200
    response_data = response.json()

    assert response_data

    for segment in response_data:
        assert "enabled" in segment
        assert "name" in segment
        assert "_id" in segment
        assert "highlight_id" in segment

    shutil.rmtree(highlight.segments_path)
