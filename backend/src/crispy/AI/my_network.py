from typing import List

import numpy
import scipy.special
import scipy.ndimage

numpy.random.seed(1)
numpy.set_printoptions(precision=2)


class neuralNetwork:
    """Neural network to predict if a kill is on the image"""

    def __init__(self, nodes: List[int], learning_rate: float) -> None:
        self.nodes = nodes
        self.learning_rate = learning_rate
        self.weights = []
        for i in range(len(nodes) - 1):
            w = numpy.random.normal(0.0, pow(nodes[i], -0.5),
                                    (nodes[i + 1], nodes[i]))
            self.weights.append(w)

        self.activation_function = lambda x: scipy.special.expit(x)

    def train(self, inputs: List[float], targets: List[float]) -> None:
        inputs = numpy.array(inputs, ndmin=2).T
        targets = numpy.array(targets, ndmin=2).T
        outputs = []
        final_inputs = []
        for i in range(len(self.nodes) - 1):
            tmp_inputs = numpy.dot(self.weights[i], inputs)
            tmp_outputs = self.activation_function(tmp_inputs)

            final_inputs.append(inputs)
            outputs.append(tmp_outputs)

            inputs = tmp_outputs

        errors = [targets - outputs[-1]]
        # -1 because we already calculated the final_errors
        # -1 because we don't want the error of the input layer
        for i in range(len(self.nodes) - 1 - 1, 0, -1):
            errors.insert(0, numpy.dot(self.weights[i].T, errors[0]))

        for i in range(len(self.nodes) - 1):
            self.weights[i] += self.learning_rate * \
                numpy.dot((errors[i] * outputs[i] *
                      (1.0 - outputs[i])), numpy.transpose(final_inputs[i]))

    def query(self, inputs: List[float]) -> List[float]:
        inputs = numpy.array(inputs, ndmin=2).T
        outputs = []
        for i in range(len(self.nodes) - 1):
            tmp_inputs = numpy.dot(self.weights[i], inputs)
            tmp_outputs = self.activation_function(tmp_inputs)

            outputs.append(tmp_outputs)

            inputs = tmp_outputs
        return outputs[-1]
