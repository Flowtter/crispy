from bson import ObjectId

from api.models.segment import Segment


async def test_get_segments_id(client, segment):
    response = await client.get(f"/segments/{segment.id}")
    assert response.status_code == 200
    segment_view = segment.view()
    segment_view["_id"] = str(segment_view["_id"])
    segment_view["highlight_id"] = str(segment_view["highlight_id"])

    assert response.json() == segment_view

    response = await client.get(f"/segments/{ObjectId()}")
    assert response.status_code == 404


async def test_get_segments_id_video(client, segment):
    response = await client.get(f"/segments/{segment.id}/video")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "video/mp4"

    response = await client.get(f"/segments/{ObjectId()}/video")
    assert response.status_code == 404


async def test_post_segments_id_switch_status(client, segment):
    response = await client.post(f"/segments/{segment.id}/switch-status")
    assert response.status_code == 200
    assert not Segment.find_one(segment.id).enabled

    response = await client.post(f"/segments/{segment.id}/switch-status")
    assert response.status_code == 200
    assert Segment.find_one(segment.id).enabled

    response = await client.post(f"/segments/{ObjectId()}/switch-status")
    assert response.status_code == 404
