from typing import List, Any, Tuple
import warnings
from datetime import datetime
import argparse
import sys
import os
import shutil

import numpy as np
import progressbar

from network import NeuralNetwork

# FIXME
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

DEBUG = False


class Trainer(NeuralNetwork):
    """Trainer for the neural network"""

    def __init__(self, nodes: List[int], learning_rate: float) -> None:
        super().__init__(nodes, learning_rate)
        value = hash(str(datetime.now()))
        value %= 1 << 12
        self.hash = str(value)

    @staticmethod
    def move_images(histogram: List[int]) -> None:
        """Debugging method to move images to the folder `issues`"""
        maximum = max(histogram)

        for f in os.listdir("./issues"):
            os.remove(os.path.join("./issues", f))

        for index, value in enumerate(histogram):
            if value >= maximum - 2:
                shutil.copy("./backend/dataset/result/" + images[index],
                            "./issues/" + images[index])

    def train(self, epochs: int, inputs: List[List[float]],
              targets: List[Any]) -> None:
        """Train the neural network for a given number of epochs"""
        last_error = float("inf")
        histogram = [0 for _ in range(len(inputs))]
        for epoch in range(epochs):
            print("===\n\tEpoch:", epoch)
            progress_bar = progressbar.ProgressBar(max_value=len(inputs))
            progress_bar.update(0)
            accuracy = 0

            for j in range(len(inputs)):
                res, _, _ = self._train(inputs[j], targets[j])
                accuracy += res
                if j % 25 == 0:
                    progress_bar.update(j)

                if res == 0:
                    histogram[j] += 1

            progress_bar.finish()
            # self.learning_rate *= 0.995

            print("Errors:", len(inputs) - accuracy)

            if epoch % 10 == 0:
                self.save("./outputs/trained_network_" + self.hash + "_" +
                          str(epoch))
                if epoch and DEBUG:
                    self.move_images(histogram)
                histogram = [0 for _ in range(len(inputs))]

            last_error = len(inputs) - accuracy
            print("Accuracy:", accuracy / len(inputs))
            if last_error == 0:
                break

        self.save("./outputs/trained_network_" + self.hash + "_end")

    def test(self, inputs: List[List[float]], targets: List[Any]) -> None:
        """Test the neural network"""
        print("Testing\nmode DEBUG =", DEBUG)
        accuracy_score = 0
        for j in range(len(inputs)):
            result = np.argmax(self.query(inputs[j]))
            accuracy_score += result == np.argmax(targets[j])
            if result != np.argmax(targets[j]):
                if DEBUG:
                    print(j)
                else:
                    print("--- Expected:", np.argmax(targets[j]), "Got:",
                          result, "at:", j)

        print("\nAccuracy:", accuracy_score / len(inputs))

    def __str__(self) -> str:
        return "hash: " + self.hash + "\n" + super().__str__()


def get_inputs_targets(path: str) -> Tuple[List[List[float]], List[Any]]:
    """Read the path csv file and return the inputs and targets"""
    with open(path, 'r') as f:
        test_data_list = f.readlines()

        final_inputs = []
        final_targets = []

        for record in test_data_list:
            all_values = record.split(',')
            inputs = (np.asfarray(all_values[1:]) / 255.0 * 0.99) + 0.01

            targets = np.zeros(2) + 0.01
            targets[int(all_values[0])] = 0.99

            final_inputs.append(inputs)
            final_targets.append(targets)
    return final_inputs, final_targets


def test(trainer: Trainer, path: str) -> None:
    """Wrapper for the test method"""
    print("=================================")
    final_inputs, final_targets = get_inputs_targets(path)
    trainer.test(final_inputs, final_targets)


def train(epoch: int, trainer: Trainer, path: str) -> None:
    """Wrapper for the train method"""
    final_inputs, final_targets = get_inputs_targets(path)
    trainer.train(epoch, final_inputs, final_targets)


if __name__ == "__main__":
    t = Trainer([7200, 120, 2], 0.001)

    csv_path = "./backend/dataset/result.csv"

    parser = argparse.ArgumentParser()
    parser.add_argument("--train",
                        help="Train the network",
                        action="store_true")
    parser.add_argument("--test", help="Test the network", action="store_true")
    parser.add_argument("--epoch",
                        help="Number of epochs",
                        type=int,
                        default=1000)
    parser.add_argument("--load",
                        help="Load a trained network",
                        action="store_true")
    parser.add_argument("--path",
                        help="Path to the network",
                        type=str,
                        default="./backend/assets/trained_network_latest.npy")

    parser.add_argument("--debug", help="Debug mode", action="store_true")

    args = parser.parse_args()

    images = []
    if args.debug:
        images = os.listdir("./backend/dataset/result")
        images.sort(key=lambda x: int(x.split("_")[0]))
        DEBUG = True

    if args.load:
        t.load(args.path)

    print(t)
    if args.train:
        train(args.epoch, t, csv_path)

    if args.test:
        if not args.load and not args.train:
            print("You need to load a trained network")
            sys.exit(1)
        test(t, csv_path)
