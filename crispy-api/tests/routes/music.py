from bson import ObjectId

from api.models.music import Music


async def test_get_musics(client, music):
    response = await client.get("/musics")
    response_data = response.json()
    assert response.status_code == 200

    assert len(response_data) == 1
    music_view = music.view()
    music_view["_id"] = str(music_view["_id"])
    assert response_data[0] == music_view


async def test_get_musics_id(client, music):
    response = await client.get(f"/musics/{music.id}")
    assert response.status_code == 200
    music_view = music.view()
    music_view["_id"] = str(music_view["_id"])
    assert response.json() == music_view

    response = await client.get(f"/musics/{ObjectId()}")
    assert response.status_code == 404


async def test_get_musics_id_music(client, music):
    response = await client.get(f"/musics/{music.id}/music")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "audio/mpeg"

    response = await client.get(f"/musics/{ObjectId()}/music")
    assert response.status_code == 404


async def test_post_musics_id_switch_status(client, music):
    response = await client.post(f"/musics/{music.id}/switch-status")
    assert response.status_code == 200
    assert not Music.find_one(music.id).enabled

    response = await client.post(f"/musics/{music.id}/switch-status")
    assert response.status_code == 200
    assert Music.find_one(music.id).enabled

    response = await client.post(f"/musics/{ObjectId()}/switch-status")
    assert response.status_code == 404


async def test_post_musics_id_move_other_music_id(client, music):
    other_music = Music({"index": 0}).save()
    assert Music.find_one(music.id).index == 1
    assert Music.find_one(other_music.id).index == 0
    response = await client.post(
        "/musics/reorder",
        json={
            "music_id": str(music.id),
            "other_music_id": str(other_music.id),
        },
    )
    assert response.status_code == 200
    assert Music.find_one(music.id).index == 0
    assert Music.find_one(other_music.id).index == 1

    assert (
        await client.post(
            "/musics/reorder",
            json={
                "music_id": str(music.id),
                "other_music_id": str(music.id),
            },
        )
    ).status_code == 400

    assert (
        await client.post(
            "/musics/reorder",
            json={
                "music_id": str(music.id),
                "other_music_id": str(ObjectId()),
            },
        )
    ).status_code == 404
