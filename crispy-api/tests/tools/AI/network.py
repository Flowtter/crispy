import os

import numpy

from api.tools.AI.network import NeuralNetwork
from api.tools.AI.trainer import get_inputs_targets
from api.tools.enums import SupportedGames
from tests.constants import CSV_PATH_OVERWATCH, OVERWATCH_NETWORK

numpy.random.seed(2)


def test_network(tmp_path, capsys):
    with capsys.disabled():
        network = NeuralNetwork(SupportedGames.OVERWATCH, 0.01)
        assert network.weights == []
        network.initialize_weights()
        assert len(network.weights) == 3

        network.load(OVERWATCH_NETWORK)

        final_inputs, final_targets = get_inputs_targets(CSV_PATH_OVERWATCH)
        for i in range(len(final_inputs)):
            result = network.query(final_inputs[i])
            assert result[numpy.argmax(final_targets[i])] > 0.9

        network.save(os.path.join(tmp_path, "test"), False)

        network2 = NeuralNetwork(SupportedGames.OVERWATCH, 0.01)
        network2.load(os.path.join(tmp_path, "test.npy"))

        assert numpy.allclose(network.weights[0], network2.weights[0])

        os.remove(os.path.join(tmp_path, "test.npy"))

    print(network)
    assert (
        capsys.readouterr().out
        == "nodes: [10000, 120, 15, 2]\nlearning_rate: 0.01\n-----\n"
    )
