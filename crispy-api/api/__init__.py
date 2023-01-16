import logging
import subprocess

import mongo_thingy
from bson import ObjectId
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from pydantic.json import ENCODERS_BY_TYPE

from api.config import DEBUG, MONGO_URI, VIDEOS
from api.tools.setup import handle_highlights

ENCODERS_BY_TYPE[ObjectId] = str


logging.getLogger("PIL").setLevel(logging.ERROR)


def init_app(debug):
    if debug:
        return FastAPI(debug=True)
    return FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


app = init_app(debug=DEBUG)


@app.on_event("startup")
async def init_database(MONGODB_NAME=None):
    mongo_thingy.connect(
        MONGO_URI, database_name=MONGODB_NAME, uuidRepresentation="standard"
    )


@app.on_event("startup")
def verify_ffmpeg_utils_are_installed() -> None:
    def is_tool_installed(ffmpeg_tool) -> None:
        try:
            subprocess.check_output([ffmpeg_tool, "-version"])
        except FileNotFoundError as e:
            raise RuntimeError(f"{ffmpeg_tool} is not installed") from e

    tools = ["ffmpeg", "ffprobe"]
    for tool in tools:
        is_tool_installed(tool)


@app.on_event("startup")
async def handle_highlights_on_startup():
    await handle_highlights(VIDEOS, "valorant", framerate=8)


@app.exception_handler(HTTPException)
def http_exception(request, exc):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


from api.routes import highlight  # noqa
