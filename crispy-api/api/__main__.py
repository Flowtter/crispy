import argparse
import asyncio
import os
import sys

import uvicorn

from api import init_database
from api.config import (
    DATASET_CSV_PATH,
    DATASET_CSV_TEST_PATH,
    DEBUG,
    HOST,
    NETWORK_OUTPUTS_PATH,
    PORT,
)
from api.tools.AI.trainer import Trainer, test, train
from api.tools.dataset import create_dataset
from api.tools.enums import SupportedGames

_parser = argparse.ArgumentParser()
# Dataset
_parser.add_argument("--dataset", action="store_true")

# Trainer
_parser.add_argument("--train", help="Train the network", action="store_true")
_parser.add_argument("--test", help="Test the network", action="store_true")
_parser.add_argument("--epoch", help="Number of epochs", type=int, default=1000)
_parser.add_argument("--load", help="Load a trained network", action="store_true")
_parser.add_argument("--path", help="Path to the network", type=str)

# Game
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
    if not _args.dataset and not _args.train and not _args.test:
        uvicorn.run("api:app", host=HOST, port=PORT, reload=DEBUG, proxy_headers=True)
    else:
        game = SupportedGames(_args.game)
        if _args.dataset:
            if not game:
                raise ValueError("Game not supported")

            asyncio.run(generate_dataset(game))
        else:
            trainer = Trainer(game, 0.01)

            if _args.load:
                trainer.load(_args.path)
            else:
                trainer.initialize_weights()

            print(trainer)
            if _args.train:
                if not os.path.exists(NETWORK_OUTPUTS_PATH):
                    os.makedirs(NETWORK_OUTPUTS_PATH)
                train(
                    _args.epoch, trainer, DATASET_CSV_PATH, True, NETWORK_OUTPUTS_PATH
                )

            if _args.test:
                if not _args.load and not _args.train:
                    print("You need to load a trained network")
                    sys.exit(1)

                sys.exit(not test(trainer, DATASET_CSV_TEST_PATH))
