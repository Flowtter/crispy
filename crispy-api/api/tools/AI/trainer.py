import argparse
import os
import sys
from datetime import datetime
from typing import Any, List, Tuple

import numpy as np
import progressbar

from api.tools.AI.network import NeuralNetwork


class Trainer(NeuralNetwork):
    """
    Trainer for the neural network
    """

    def __init__(self, nodes: List[int], learning_rate: float) -> None:
        super().__init__(nodes, learning_rate)
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

            for j in range(len(inputs)):
                res, _, _ = self._train(inputs[j], targets[j])
                accuracy += res
                if not res:
                    print(
                        "Failed:",
                        j,
                        "Got:",
                        res,
                        "Expected:",
                        np.argmax(targets[j]),
                        "Inputs:",
                        inputs[j],
                    )

                if j % 25 == 0:
                    progress_bar.update(j)

            progress_bar.finish()

            print("Errors:", len(inputs) - accuracy)
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

    def test(self, inputs: List[List[float]], targets: List[Any], con_min=0.95) -> bool:
        """
        Test the neural network
        """
        print("Testing...")
        accuracy_score = 0
        failed = []
        confidence = 0
        mini_confidence = 100
        for j in range(len(inputs)):
            q = self.query(inputs[j])
            confidence += np.max(q)
            mini_confidence = min(mini_confidence, np.max(q))
            result = np.argmax(q)

            accuracy_score += result == np.argmax(targets[j])
            if result != np.argmax(targets[j]):
                failed.append(j)
                print(
                    "--- Expected:",
                    np.argmax(targets[j]),
                    "Got:",
                    result,
                    "at:",
                    j,
                    "confidence:",
                    str(int(np.max(q) * 100)) + "%",
                    "inputs:",
                    inputs[j],
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


def train(epoch: int, trainer: Trainer, path: str, save: bool, output_path) -> None:
    """
    Wrapper for the train method
    """
    final_inputs, final_targets = get_inputs_targets(path)
    trainer.train(epoch, final_inputs, final_targets, save, output_path)


if __name__ == "__main__":  # pragma: no cover
    t = Trainer([4000, 120, 15, 2], 0.01)
    csv_path = os.path.join("backend", "dataset", "result.csv")
    csv_test_path = os.path.join("backend", "dataset", "test.csv")

    parser = argparse.ArgumentParser()
    parser.add_argument("--train", help="Train the network", action="store_true")
    parser.add_argument("--test", help="Test the network", action="store_true")
    parser.add_argument("--epoch", help="Number of epochs", type=int, default=1000)
    parser.add_argument("--load", help="Load a trained network", action="store_true")
    parser.add_argument("--path", help="Path to the network", type=str)

    parser.add_argument("--debug", help="Debug mode", action="store_true")

    args = parser.parse_args()

    images = []
    if args.debug:
        images = os.listdir("./backend/dataset/result")
        images.sort(key=lambda x: int(x.split("_")[0]))

    if args.load:
        t.load(args.path)
    else:
        t.initialize_weights()

    print(t)
    if args.train:
        train(args.epoch, t, csv_path, True, "outputs")

    if args.test:
        if not args.load and not args.train:
            print("You need to load a trained network")
            sys.exit(1)

        sys.exit(not test(t, csv_test_path))
