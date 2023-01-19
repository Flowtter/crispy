import logging
import os
import shutil
import subprocess
from typing import Callable, List, Optional, Tuple

import ffmpeg
from mongo_thingy import Thingy
from PIL import Image, ImageFilter, ImageOps

from api.config import BACKUP, DOT_PATH
from api.models.segment import Segment
from api.tools.audio import silence_if_no_audio
from api.tools.enums import SupportedGames
from api.tools.ffmpeg import merge_videos

logger = logging.getLogger("crispy")


class Highlight(Thingy):
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
        self.save()
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
        self.save()

        return True

    async def extract_overwatch_images(self, framerate: int = 4) -> bool:
        def post_process(image: Image) -> Image:
            r, g, b = image.split()
            for x in range(image.width):
                for y in range(image.height):
                    red = r.getpixel((x, y))
                    green = g.getpixel((x, y))
                    blue = b.getpixel((x, y))
                    if red > 200 and green < 100 and blue < 100:
                        r.putpixel((x, y), 255)
                        b.putpixel((x, y), 255)
                        g.putpixel((x, y), 255)
                    elif red > 200 and green < 180 and blue < 180:
                        r.putpixel((x, y), min(255, int(red * 1.5)))
                        g.putpixel((x, y), max(0, int(green * 0.3)))
                        b.putpixel((x, y), max(0, int(blue * 0.3)))
                    else:
                        r.putpixel((x, y), min(255, int(red * 1.1)))
                        g.putpixel((x, y), max(0, int(green * 0.05)))
                        b.putpixel((x, y), max(0, int(blue * 0.05)))

            # FIXME: pretty sure i can return now
            im = ImageOps.grayscale(Image.merge("RGB", (r, g, b)))

            final = Image.new("RGB", (100, 100))
            final.paste(im, (0, 0))
            return final

        return await self.extract_images(
            post_process, (910, 490, 100, 100), framerate=framerate
        )

    async def extract_valorant_images(self, framerate: int = 4) -> bool:
        def _apply_filter_and_do_operations(
            image: Image, image_filter: ImageFilter
        ) -> Image:
            image = image.filter(image_filter)

            image = image.crop((1, 1, image.width - 2, image.height - 2))

            dot = Image.open(DOT_PATH)

            image.paste(dot, (0, 0), dot)

            left = image.crop((0, 0, 25, 60))
            right = image.crop((95, 0, 120, 60))

            final = Image.new("RGB", (50, 60))
            final.paste(left, (0, 0))
            final.paste(right, (25, 0))

            final = final.crop((00, 20, 50, 60))

            return final

        def post_process(image: Image) -> Image:
            image = ImageOps.grayscale(image)

            edges = _apply_filter_and_do_operations(image, ImageFilter.FIND_EDGES)
            enhanced = _apply_filter_and_do_operations(
                image, ImageFilter.EDGE_ENHANCE_MORE
            )
            final = Image.new("RGB", (50, 80))
            final.paste(edges, (0, 0))
            enhanced = enhanced.transpose(Image.FLIP_TOP_BOTTOM)
            final.paste(enhanced, (0, 40))
            return final

        return await self.extract_images(
            post_process, (899, 801, 122, 62), framerate=framerate
        )

    async def extract_images_from_game(
        self, game: SupportedGames, framerate: int = 4
    ) -> bool:
        if game == SupportedGames.OVERWATCH:
            return await self.extract_overwatch_images(framerate)
        elif game == SupportedGames.VALORANT:
            return await self.extract_valorant_images(framerate)
        else:
            raise NotImplementedError

    def __segment(self, start: float, end: float, save_path: str) -> None:
        """
        Segment a video into a smaller video

        We get the next keyframe after the start time
        - If the next keyframe is after the end time, there is no optimization possible
            we cut from the start time to the end time and encode
        - If the next keyframe is before the end time,
            we cut from the start time to the next keyframe and encode
            we cut without encoding from the next keyframe to the end time if the end time
            we merge the two videos

        :param start: Start of the segment in seconds
        :param end: End of the segment in seconds

        :return: Path to the segmented video
        """
        next_keyframe = self.keyframes[0]
        for keyframe in self.keyframes:
            if keyframe > start:
                next_keyframe = keyframe
                break

        # FIXME: should be parameters
        video = ffmpeg.input(self.path)
        audio = silence_if_no_audio(video.audio, self.path)

        if next_keyframe > end or end - start < 1:
            # No optimization possible
            (
                ffmpeg.input(self.path)
                .output(
                    video,
                    audio,
                    save_path,
                    ss=f"{start}",
                    to=f"{end}",
                )
                .overwrite_output()
                .run(quiet=True)
            )
        else:
            # Optimization possible
            save_path_no_extension, extension = os.path.splitext(save_path)

            paths = [
                f"{save_path_no_extension}_1{extension}",
                f"{save_path_no_extension}_2{extension}",
            ]

            (
                ffmpeg.input(self.path)
                .output(
                    video,
                    audio,
                    paths[1],
                    ss=f"{next_keyframe}",
                    vcodec="copy",
                    map="0",
                    to=f"{end}",
                )
                .overwrite_output()
                .run(quiet=True)
            )

            if next_keyframe == start or next_keyframe - start < 0.2:
                os.rename(paths[1], save_path)
            else:
                (
                    ffmpeg.input(self.path)
                    .output(
                        video,
                        audio,
                        paths[0],
                        ss=f"{start}",
                        to=f"{next_keyframe}",
                    )
                    .overwrite_output()
                    .run(quiet=True)
                )
                merge_videos(
                    paths,
                    save_path,
                    True,
                )

    async def segment(self, timestamps: List[Tuple[float, float]]) -> List[Segment]:
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

        old_segments = Segment.find({"highlight_id": self.id}).to_list(0)

        # Make a list of timestamps that are new, not in the database
        new_timestamps = []
        for start, end in timestamps:
            if not any(
                old_segment.start == start and old_segment.end == end
                for old_segment in old_segments
            ):
                new_timestamps.append((start, end))

        # Delete old segments, ones that are not in the timestamps list
        segments = []
        for old_segment in old_segments:
            if not any(
                old_segment.start == start and old_segment.end == end
                for start, end in timestamps
            ):
                os.remove(old_segment.path)
                Segment.delete_one({"_id": old_segment.id})
            else:
                segments.append(old_segment)

        for (start, end) in new_timestamps:
            segment_save_path = os.path.join(self.segments_path, f"{start}-{end}.mp4")
            self.__segment(start, end, segment_save_path)
            segment = Segment(
                {
                    "highlight_id": self.id,
                    "path": segment_save_path,
                    "start": start,
                    "end": end,
                }
            )
            segment.save()
            segments.append(segment)

        return segments

    async def scale_video(
        self, width: int = 1920, height: int = 1080, backup: str = BACKUP
    ) -> None:
        """
        Scale (up or down) a video.

        :param width: Width of the video
        :param height: Height of the video
        :param backup: Path to the backup folder
        """
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"{self.path} not found")

        logger.warning(
            f"\nWARNING:Scaling video {self.path}, saving a backup in ./backup"
        )

        if not os.path.exists(backup):
            os.makedirs(backup)

        backup_path = os.path.join(backup, os.path.basename(self.path))
        shutil.move(self.path, backup_path)

        video = ffmpeg.input(backup_path)
        audio = silence_if_no_audio(video.audio, backup_path)

        video = video.filter("scale", w=width, h=height)

        ffmpeg.output(video, audio, self.path, start_number=0).run(quiet=True)

    async def remove(self) -> None:
        """
        Delete the video and all its segments
        """
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)

        Segment.delete_many({"highlight_id": self.id})
        self.__class__.delete_one(self.id)

    async def extract_keyframes(self) -> None:
        """
        Extract keyframes from the video using ffprobe
        """
        self.keyframes = []
        try:
            video_info = subprocess.check_output(
                [
                    "ffprobe",
                    "-loglevel",
                    "error",
                    "-show_frames",
                    "-select_streams",
                    "v",
                    self.path,
                ]
            ).decode("utf-8")

            for line in video_info.splitlines():
                if line.startswith("pkt_pts_time=") or line.startswith("pts_time="):
                    self.keyframes.append(float(line.split("=")[1]))
        except subprocess.CalledProcessError:
            logger.error(f"Error extracting keyframes from {self.path}")

        # 0 Is always a keyframe in mp4 files
        if not self.keyframes:
            self.keyframes = [0]

        self.save()
