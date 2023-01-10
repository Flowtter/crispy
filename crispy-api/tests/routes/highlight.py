async def test_get_video(client):
    for i in range(2):
        response = await client.get("/highlight")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["new"] == (i == 0)
        assert response_data["highlight"]["title"] == "My highlight"
