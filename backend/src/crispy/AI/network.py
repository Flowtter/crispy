from typing import List, Tuple, Any

import numpy as np
import scipy.special
import scipy.ndimage


class NeuralNetwork:
    """Neural network to predict if a kill is on the image"""

    def __init__(self, nodes: List[int], learning_rate: float) -> None:
        self.nodes = nodes
        self.learning_rate = learning_rate
        self.weights: List[Any] = []
        self.activation_function = lambda x: scipy.special.expit(x)

    def initialize_weights(self) -> None:
        """Initialize the weights of the neural network"""
        for i in range(len(self.nodes) - 1):
            w = np.random.normal(0.0, pow(self.nodes[i], -0.5),
                                 (self.nodes[i + 1], self.nodes[i]))
            self.weights.append(w)

    def _train(self, inputs: List[float],
               targets: Any) -> Tuple[int, int, int]:
        """Train the neural network"""

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

        # if expected == got:
        # return 1, expected, got

        errors = [targets - outputs[-1]]

        # -1 because we already calculated the final_errors
        # -1 because we don't want the error of the input layer
        for i in range(len(self.nodes) - 1 - 1, 0, -1):
            errors.insert(0, np.dot(self.weights[i].T, errors[0]))

        # ten times more likely to be not be kill
        # so we mitigate the error
        if expected == 0:
            errors = [e / 5 for e in errors]

        for i in range(len(self.nodes) - 1):
            self.weights[i] += self.learning_rate * \
                np.dot((errors[i] * outputs[i] *
                      (1.0 - outputs[i])), np.transpose(final_inputs[i]))

        return expected == got, expected, got

    def mean_weights(self, N: "NeuralNetwork") -> None:
        """Mitigate the weights of the current network with the weights of N"""
        for i in range(len(self.weights)):
            self.weights[i] = (self.weights[i] + N.weights[i]) / 2

    def query(self, inputs: List[float]) -> List[float]:
        """Query the neural network on a given input"""
        inputs = np.array(inputs, ndmin=2).T

        outputs = []
        for i in range(len(self.nodes) - 1):
            tmp_inputs = np.dot(self.weights[i], inputs)
            tmp_outputs = self.activation_function(tmp_inputs)

            outputs.append(tmp_outputs)

            inputs = tmp_outputs
        return outputs[-1]

    def save(self, filename: str) -> None:
        """Save the weights of the neural network in numpy format"""
        print(f"Saving weights to {filename}.npy")
        np.save(filename, self.weights)

    def load(self, filename: str) -> None:
        """Load the weights of the neural network from numpy format"""
        self.weights = np.load(filename, allow_pickle=True)

    def __str__(self) -> str:
        return f"nodes: {self.nodes}\nlearning_rate: {self.learning_rate}\n-----"
