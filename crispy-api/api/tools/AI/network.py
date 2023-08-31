from typing import Any, List, Tuple

import numpy as np
import scipy.special

from api.tools.enums import SupportedGames

NetworkResolution = {
    SupportedGames.VALORANT: [4000, 120, 15, 2],
    SupportedGames.OVERWATCH: [10000, 120, 15, 2],
    SupportedGames.CSGO2: [10000, 120, 15, 2],
}


class NeuralNetwork:
    """
    Neural network to predict if a kill is on the image
    """

    def __init__(self, game: SupportedGames, learning_rate: float = 0.01) -> None:
        self.nodes = NetworkResolution[game]
        self.learning_rate = learning_rate
        self.weights: List[Any] = []
        self.activation_function = lambda x: scipy.special.expit(x)

    def initialize_weights(self) -> None:
        """
        Initialize the weights of the neural network
        """
        for i in range(len(self.nodes) - 1):
            w = np.random.normal(
                0.0, pow(self.nodes[i], -0.5), (self.nodes[i + 1], self.nodes[i])
            )
            self.weights.append(w)

        self.weights = np.array(self.weights, dtype=object)

    def _train(self, inputs: List[float], targets: Any) -> Tuple[int, int, int]:
        """
        Train the neural network
        """
        inputs = np.array(inputs, ndmin=2).T
        targets = np.array(targets, ndmin=2).T

        outputs = []
        final_inputs = []
        for i in range(len(self.nodes) - 1):
            tmp_inputs = np.dot(self.weights[i], inputs)
            tmp_outputs = self.activation_function(tmp_inputs)

            final_inputs.append(inputs)
            outputs.append(tmp_outputs)

            inputs = tmp_outputs

        expected = int(np.argmax(targets))
        got = int(np.argmax(outputs[-1]))

        errors = [targets - outputs[-1]]

        # -1 because we already calculated the final_errors
        # -1 because we don't want the error of the input layer
        for i in range(len(self.nodes) - 1 - 1, 0, -1):
            errors.insert(0, np.dot(self.weights[i].T, errors[0]))

        # five times more likely to be not be kill
        # so we mitigate the error
        if expected == 0:
            errors = [e / 5 for e in errors]

        for i in range(len(self.nodes) - 1):
            self.weights[i] += self.learning_rate * np.dot(
                (errors[i] * outputs[i] * (1.0 - outputs[i])),
                np.transpose(final_inputs[i]),
            )

        return expected == got, expected, got

    def query(self, inputs: List[float]) -> List[float]:
        """
        Query the neural network on a given input
        """
        inputs = np.array(inputs, ndmin=2).T

        outputs: List[List[float]] = []
        for i in range(len(self.nodes) - 1):
            tmp_inputs = np.dot(self.weights[i], inputs)
            tmp_outputs = self.activation_function(tmp_inputs)

            outputs.append(tmp_outputs)

            inputs = tmp_outputs
        return outputs[-1]

    def save(self, filename: str, log: bool = True) -> None:
        """
        Save the weights of the neural network in numpy format
        """
        if log:
            print(f"Saving weights to {filename}.npy")
        np.save(filename, self.weights)

    def load(self, filename: str) -> None:
        """
        Load the weights of the neural network from numpy format
        """
        self.weights = np.load(filename, allow_pickle=True)

    def __str__(self) -> str:
        return f"nodes: {self.nodes}\nlearning_rate: {self.learning_rate}\n-----"
