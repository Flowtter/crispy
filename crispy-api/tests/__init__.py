from fastapi import HTTPException

from api import app


async def test_fastapi(client):
    @app.get("/protected")
    async def get_protected():
        raise HTTPException(403)

    @app.get("/health")
    async def get_health():
        return {"status": "ok"}

    response = await client.get("/protected")
    assert response.status_code == 403

    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
