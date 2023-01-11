import os
from typing import Callable, List, Optional, Tuple

import ffmpeg
from mongo_thingy import AsyncThingy
from PIL import Image

from api.tools.audio import silence_if_no_audio


class Highlight(AsyncThingy):
    segments_path: Optional[str]

    async def extract_thumbnail(self) -> bool:
        """
        Extract the first image of a video

        :param highlight: Highlight to extract the image from
        """

        if self.thumbnail_path:
            return False

        thumbnail_path = os.path.join(self.directory, "thumbnail.jpg")
        ffmpeg.input(self.path).output(thumbnail_path, vframes=1).run(quiet=True)

        self.update({"thumbnail_path": thumbnail_path})
        await self.save()
        return True

    async def extract_images(
        self,
        post_process: Callable,
        coordinates: Tuple,
        framerate: int = 4,
    ) -> bool:
        """
        Extracts images from a video at a given framerate

        :param post_process: Function to apply to each image
        :param framerate: Framerate to extract the images

        """
        if self.images_path:
            return False
        images_path = os.path.join(self.directory, "images")

        if not os.path.exists(images_path):
            os.mkdir(images_path)
            (
                ffmpeg.input(self.path)
                .filter("fps", fps=f"1/{round(1 / framerate, 5)}")
                .crop(*coordinates)
                .output(os.path.join(images_path, "%8d.bmp"), start_number=0)
                .run(quiet=True)
            )

        images = os.listdir(images_path)
        images.sort(key=lambda x: int(x.split(".")[0]))

        for image in images:
            im_path = os.path.join(images_path, image)
            im: Image = Image.open(im_path)

            post_process(im).save(im_path)

        self.update({"images_path": images_path})
        await self.save()

        return True

    # FIXME: currently this function is recalculating the video
    # using -vcodec copy, should be able to fix this
    # but ffmpeg-python doesn't support it
    # moreover, we're probably going to use a different file format
    async def segment(self, timestamps: List[Tuple[float, float]]) -> List[str]:
        """
        Segment a video into multiple videos

        :param timestamps: List of tuples containing the start
            and end of the segment in seconds

        :return: List of paths to the segmented videos
        """
        if not self.segments_path:
            self.segments_path = os.path.join(self.directory, "segments")

        if not os.path.exists(self.segments_path):
            os.mkdir(self.segments_path)

        segments = []

        for (start, end) in timestamps:
            video = ffmpeg.input(self.path)

            video_save_path = os.path.join(self.segments_path, f"{start}-{end}.mp4")

            audio = silence_if_no_audio(video.audio, self.path)
            video = ffmpeg.output(
                video,
                audio,
                video_save_path,
                ss=f"{start}",
                to=f"{end}",
                preset="ultrafast",
            )
            video = video.overwrite_output()
            video.run(quiet=True)

            segments.append(video_save_path)

        return segments
