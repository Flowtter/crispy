from typing import List

import logging

from utils.arguments import args
from utils.constants import NEURAL_NETWORK_PATH
from utils.IO.io import generate_tmp_architecture
import video.video as vid
from AI.network import NeuralNetwork

logging.getLogger("PIL").setLevel(logging.ERROR)


def main(videos: List[str]) -> None:
    nn = NeuralNetwork([4000, 120, 15, 2], 0.01)
    nn.load(NEURAL_NETWORK_PATH)
    l.debug(f"Neural network: {nn}")

    generate_tmp_architecture(not args.no_extract)

    for video in videos:
        l.info(f"Currently processing {video}")

        if not args.no_extract:
            images_path = vid.extract_frames_from_video(video, 8)
        else:
            images_path = vid.get_saving_path(video)

        query_array = vid.get_query_array_from_video(nn, images_path)

        print(query_array)


if __name__ == "__main__":
    l = logging.getLogger()

    print("Welcome to crispy!")

    l.info("Starting the program crispy")

    l.debug(f"Arguments: {args}")

    videos_path = ["0.mp4"]

    # FIXME: should be sort with the frontend ?
    videos_path.sort()

    main(videos_path)
