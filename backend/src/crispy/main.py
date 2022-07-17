import logging
from typing import List

from utils.arguments import args
from utils.constants import NEURAL_NETWORK_PATH
from utils.IO import io
import video.video as vid
from AI.network import NeuralNetwork

logging.getLogger("PIL").setLevel(logging.ERROR)


def main(videos: List[str]) -> None:
    ### FIXME: should be settings in settings.json
    framerate = 8
    second_before = 2.5
    second_after = 1.5
    #### FIXME: should not be parameters to function
    frames_before = int(second_before * framerate)
    frames_after = int(second_after * framerate)

    io.generate_tmp_folder(not args.no_extract)

    nn = NeuralNetwork([4000, 120, 15, 2], 0.01)
    nn.load(NEURAL_NETWORK_PATH)
    l.debug(f"Neural network: {nn}")

    for video in videos:
        l.info(f"Currently processing {video}")
        video_no_ext = io.remove_extension(video)
        video_clean_name = io.generate_clean_name(video_no_ext)
        l.debug(f"Clean name: {video_clean_name}")

        if not args.no_extract:
            io.generate_folder_clip(video_clean_name)
            images_path = vid.extract_frames_from_video(video, framerate)
        else:
            images_path = vid.get_saving_path(video_clean_name)

        if not args.no_segmentation:
            io.clean_cuts(video_clean_name)

            query_array = vid.get_query_array_from_video(nn, images_path)
            kill_array = vid.get_kill_array_from_query_array(
                query_array, frames_before, frames_after)

            vid.segment_video_with_kill_array(video, kill_array, framerate)


if __name__ == "__main__":
    l = logging.getLogger()

    print("Welcome to crispy!")

    l.info("Starting the program crispy")

    l.debug(f"Arguments: {args}")

    videos_path = ["0.mp4"]

    # FIXME: should be sort with the frontend ?
    videos_path.sort()

    main(videos_path)
