import argparse
import asyncio

import uvicorn

from api import init_database
from api.config import DEBUG, HOST, PORT
from api.tools.dataset import create_dataset
from api.tools.enums import SupportedGames

_parser = argparse.ArgumentParser()
_parser.add_argument("--dataset", action="store_true")
_parser.add_argument(
    "--game", type=str, choices=[game.value for game in SupportedGames]
)

_args = _parser.parse_args()


async def generate_dataset(game: SupportedGames) -> None:
    """
    Generate a dataset from the highlights
    """
    init_database(".dataset")
    await create_dataset(game)


if __name__ == "__main__":
    if not _args.dataset:
        uvicorn.run("api:app", host=HOST, port=PORT, reload=DEBUG, proxy_headers=True)
    else:
        game = SupportedGames(_args.game)
        if not game:
            raise ValueError("Game not supported")

        asyncio.run(generate_dataset(game))
