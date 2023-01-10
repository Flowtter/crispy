import uvicorn

from api.config import DEBUG, HOST, PORT

if __name__ == "__main__":
    uvicorn.run("api:app", host=HOST, port=PORT, reload=DEBUG, proxy_headers=True)
