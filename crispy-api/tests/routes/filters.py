from bson import ObjectId

from api.models.filter import Filter


async def test_get_filters_highlight_id(client, filter_h):
    response = await client.get("/filters/global")
    response_data = response.json()
    assert response.status_code == 200
    del response_data["_id"]
    assert response_data == {
        "global": True,
    }

    response = await client.get(f"/filters/{filter_h.highlight_id}")
    response_data = response.json()
    assert response.status_code == 200

    del response_data["_id"]
    assert response_data == {
        "highlight_id": str(filter_h.highlight_id),
    }

    response = await client.get(f"/filters/{ObjectId()}")
    assert response.status_code == 404


async def test_post_filters_highlight_id(client, filter_h):
    json = {
        "blur": {"box": True, "value": 1.0},
        "hflip": {"box": True},
        "vflip": {"box": True},
        "saturation": {"box": True, "value": 1.0},
        "brightness": {"box": True, "value": 1.0},
        "zoom": {"box": True, "value": 1.0},
        "grayscale": {"box": True},
    }
    filters = {
        "blur": 1.0,
        "hflip": True,
        "vflip": True,
        "saturation": 1.0,
        "brightness": 1.0,
        "zoom": 1.0,
        "grayscale": True,
    }

    response = await client.post(f"/filters/{filter_h.highlight_id}", json=json)
    response_data = response.json()
    assert response.status_code == 200
    del response_data["_id"]
    assert response_data == {
        "highlight_id": str(filter_h.highlight_id),
        "filters": filters,
    }

    response = await client.post("/filters/global", json=json)
    assert response.status_code == 404

    response = await client.get("/filters/global")
    assert response.status_code == 200
    response = await client.post("/filters/global", json=json)
    response_data = response.json()
    assert response.status_code == 200
    del response_data["_id"]
    assert response_data == {
        "global": True,
        "filters": filters,
    }

    response = await client.post(f"/filters/{ObjectId()}", json=json)
    assert response.status_code == 404

    response = await client.post(f"/filters/{filter_h.highlight_id}/update")
    assert response.status_code == 200
    response = await client.post(f"/filters/{filter_h.highlight_id}", json=json)
    response_data = response.json()
    assert response.status_code == 200
    del response_data["_id"]
    assert response_data == {
        "highlight_id": str(filter_h.highlight_id),
        "filters": filters,
        "updating": False,
    }


async def test_post_filters_highlight_id_update(client, filter_h):
    response = await client.post(f"/filters/{filter_h.highlight_id}/update")
    assert response.status_code == 200

    filter_h = Filter.find_one({"highlight_id": filter_h.highlight_id})
    assert filter_h.updating is True

    response = await client.post(f"/filters/{ObjectId()}/update")
    assert response.status_code == 404

    response = await client.post("/filters/global/update")
    assert response.status_code == 403
