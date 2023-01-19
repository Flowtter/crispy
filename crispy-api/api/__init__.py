import logging
import subprocess
from typing import Optional

from bson import ObjectId
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from mongo_thingy import connect
from montydb import MontyClient, set_storage
from pydantic.json import ENCODERS_BY_TYPE

from api.config import DATABASE_PATH, DEBUG, VIDEOS
from api.tools.enums import SupportedGames
from api.tools.setup import handle_highlights

ENCODERS_BY_TYPE[ObjectId] = str


logging.getLogger("PIL").setLevel(logging.ERROR)


def init_app(debug: bool) -> FastAPI:
    if debug:
        return FastAPI(debug=True)
    return FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


app = init_app(debug=DEBUG)


@app.on_event("startup")
def init_database(path: Optional[str] = DATABASE_PATH) -> None:
    set_storage(path, storage="sqlite")
    connect(path, client_cls=MontyClient)


@app.on_event("startup")
def verify_ffmpeg_utils_are_installed() -> None:
    def is_tool_installed(ffmpeg_tool: str) -> None:
        try:
            subprocess.check_output([ffmpeg_tool, "-version"])
        except FileNotFoundError as e:
            raise RuntimeError(f"{ffmpeg_tool} is not installed") from e

    tools = ["ffmpeg", "ffprobe"]
    for tool in tools:
        is_tool_installed(tool)


@app.on_event("startup")
async def handle_highlights_on_startup() -> None:
    await handle_highlights(VIDEOS, SupportedGames.VALORANT, framerate=8)


@app.exception_handler(HTTPException)
def http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


from api.routes import highlight  # noqa
