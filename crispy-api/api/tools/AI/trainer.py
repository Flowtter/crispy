import os
from datetime import datetime
from typing import Any, List, Tuple

import numpy as np
import progressbar

from api.tools.AI.network import NeuralNetwork
from api.tools.enums import SupportedGames


class Trainer(NeuralNetwork):
    """
    Trainer for the neural network
    """

    def __init__(self, game: SupportedGames, learning_rate: float) -> None:
        super().__init__(game, learning_rate)
        value = hash(str(datetime.now()))
        value %= 1 << 12
        self.hash = str(value)

    def train(
        self,
        epochs: int,
        inputs: List[List[float]],
        targets: List[Any],
        save: bool,
        output_path: str,
    ) -> None:
        """
        Train the neural network for a given number of epochs
        """
        for epoch in range(epochs):
            print("===\n\tEpoch:", epoch)
            progress_bar = progressbar.ProgressBar(max_value=len(inputs))
            progress_bar.update(0)
            accuracy = 0
            failed = 0

            for i in range(len(inputs)):
                res, expected, got = self._train(inputs[i], targets[i])
                accuracy += res
                if not res:
                    failed += 1
                    print(
                        "Failed:",
                        i,
                        "Got:",
                        got,
                        "Expected:",
                        expected,
                    )

                if i % 25 == 0:
                    progress_bar.update(i)

            progress_bar.finish()

            print("Errors:", failed)
            print("Accuracy:", accuracy / len(inputs))

            if epoch % 25 == 0 and save:
                self.save(
                    os.path.join(
                        output_path, "trained_network_" + self.hash + "_" + str(epoch)
                    )
                )

        if save:
            self.save(
                os.path.join(output_path, "trained_network_" + self.hash + "_end")
            )

    def test(self, inputs: List[List[float]], targets: List[Any]) -> bool:
        """
        Test the neural network
        """
        accuracy_score = 0
        confidence = 0
        mini_confidence = 100
        for j in range(len(inputs)):
            q = self.query(inputs[j])
            confidence += np.max(q)
            mini_confidence = min(mini_confidence, np.max(q))
            result = np.argmax(q)

            accuracy_score += result == np.argmax(targets[j])
            if result != np.argmax(targets[j]):
                print(
                    "--- Expected:",
                    np.argmax(targets[j]),
                    "Got:",
                    result,
                    "at:",
                    j,
                    "confidence:",
                    str(int(np.max(q) * 100)) + "%",
                )

        acc = accuracy_score / len(inputs)
        con = confidence / len(inputs)
        print("\nAccuracy:", round(acc, 5) * 100, "%")
        print("Confidence:", round(con, 5) * 100, "%")
        print("Mini confidence:", mini_confidence * 100)

        return acc > 0.98 and con > 0.85

    def __str__(self) -> str:
        return "hash: " + self.hash + "\n" + super().__str__()


def get_inputs_targets(path: str) -> Tuple[List[List[float]], List[Any]]:
    """
    Read the path csv file and return the inputs and targets
    """
    with open(path, "r") as f:
        test_data_list = f.readlines()

        final_inputs = []
        final_targets = []

        for record in test_data_list:
            all_values = record.split(",")
            inputs = (np.asfarray(all_values[1:]) / 255.0 * 0.99) + 0.01

            targets = np.zeros(2) + 0.01
            targets[int(all_values[0])] = 0.99

            final_inputs.append(inputs)
            final_targets.append(targets)

    return final_inputs, final_targets


def test(trainer: Trainer, path: str) -> bool:
    """
    Wrapper for the test method
    """
    final_inputs, final_targets = get_inputs_targets(path)
    return trainer.test(final_inputs, final_targets)


def train(
    epoch: int, trainer: Trainer, path: str, save: bool, output_path: str
) -> None:
    """
    Wrapper for the train method
    """
    final_inputs, final_targets = get_inputs_targets(path)
    trainer.train(epoch, final_inputs, final_targets, save, output_path)
