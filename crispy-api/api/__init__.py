import logging
import os
import subprocess
from typing import Optional

from bson import ObjectId
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mongo_thingy import connect
from montydb import MontyClient, set_storage
from pydantic.json import ENCODERS_BY_TYPE

from api.config import (
    ASSETS,
    DATABASE_PATH,
    DEBUG,
    FRAMERATE,
    GAME,
    MUSICS,
    USE_NETWORK,
    VIDEOS,
)
from api.tools.AI.network import NeuralNetwork
from api.tools.enums import SupportedGames
from api.tools.filters import apply_filters  # noqa
from api.tools.setup import handle_highlights, handle_musics
from api.tools.utils import download_champion_images

ENCODERS_BY_TYPE[ObjectId] = str

NEURAL_NETWORK = None

if USE_NETWORK:
    NEURAL_NETWORK = NeuralNetwork(GAME)
    NEURAL_NETWORK.load(os.path.join(ASSETS, GAME + ".npy"))


logging.getLogger("PIL").setLevel(logging.ERROR)


def init_app(debug: bool) -> FastAPI:
    if debug:
        logger = logging.getLogger("uvicorn")
        logger.setLevel(logging.DEBUG)
        logger.debug("Crispy started in debug mode")
        return FastAPI(debug=True)
    return FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


app = init_app(debug=DEBUG)


@app.on_event("startup")
def init_database(path: Optional[str] = DATABASE_PATH) -> None:
    set_storage(path)
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
async def setup_crispy() -> None:
    await handle_musics(MUSICS)
    await handle_highlights(VIDEOS, GAME, framerate=FRAMERATE)
    if GAME == SupportedGames.LEAGUE_OF_LEGENDS:
        await download_champion_images()


@app.exception_handler(HTTPException)
def http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


from api.routes import filters, highlight, music, result, segment  # noqa
