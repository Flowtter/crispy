from typing import List

from utils.arguments import args
from utils.constants import NEURAL_NETWORK_PATH, L
from utils.IO import io
import video.video as vid
from AI.network import NeuralNetwork


def main(videos: List[str]) -> None:
    io.generate_tmp_folder(not args.no_extract)

    nn = NeuralNetwork([4000, 120, 15, 2], 0.01)
    nn.load(NEURAL_NETWORK_PATH)
    L.debug(f"Neural network: {nn}")

    for video in videos:
        L.info(f"Currently processing {video}")
        video_no_ext = io.remove_extension(video)
        video_clean_name = io.generate_clean_name(video_no_ext)
        L.debug(f"Clean name: {video_clean_name}")

        if not args.no_extract:
            io.generate_folder_clip(video_clean_name)
            images_path = vid.extract_frames_from_video(video)
        else:
            images_path = vid.get_saving_path(video_clean_name)

        if not args.no_segmentation:
            io.clean_cuts(video_clean_name)
            print(images_path)
            query_array = vid.get_query_array_from_video(nn, images_path)
            L.debug(query_array)
            kill_array = vid.get_kill_array_from_query_array(query_array)
            L.debug(kill_array)
            kill_array = vid.post_processing_kill_array(kill_array)
            L.debug(kill_array)
            vid.segment_video_with_kill_array(video, kill_array)

    if not args.no_merge:
        L.info("Merging videos")
        vid.merge_cuts()


if __name__ == "__main__":
    print("Welcome to crispy!")

    L.info("Starting the program crispy")

    L.debug(f"Arguments: {args}")

    videos_path = ["1.mp4"]

    # FIXME: should be sort with the frontend ?
    videos_path.sort()

    main(videos_path)
