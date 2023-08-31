import os
import shutil

import numpy

from api.tools.AI.network import NetworkResolution
from api.tools.AI.trainer import Trainer
from api.tools.AI.trainer import test as trainer_test
from api.tools.AI.trainer import train
from api.tools.enums import SupportedGames
from tests.constants import CSV_PATH_XOR

SupportedGames.XOR = "xor"
NetworkResolution[SupportedGames.XOR] = [2, 4, 2]

numpy.random.seed(2)


def test_trainer(capsys, tmp_path):
    trainer = Trainer(SupportedGames.XOR, 0.1)
    trainer.initialize_weights()

    assert not trainer_test(trainer, CSV_PATH_XOR)

    train(5000, trainer, CSV_PATH_XOR, False, tmp_path)

    assert trainer_test(trainer, CSV_PATH_XOR)

    train(30, trainer, CSV_PATH_XOR, True, tmp_path)

    assert len(os.listdir(tmp_path)) == 3

    shutil.rmtree(tmp_path)
    os.mkdir(tmp_path)


def test_print(capsys):
    trainer = Trainer(SupportedGames.XOR, 0.1)
    trainer.hash = "test"

    print(trainer)
    assert (
        capsys.readouterr().out
        == "hash: test\nnodes: [2, 4, 2]\nlearning_rate: 0.1\n-----\n"
    )
