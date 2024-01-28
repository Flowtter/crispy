import logging
import os
import shutil
from typing import Any, Callable, Dict, List, Optional, Tuple

import ffmpeg
from mongo_thingy import Thingy
from PIL import Image, ImageFilter, ImageOps

from api.config import BACKUP, CSGO2_MASK_PATH, VALORANT_MASK_PATH
from api.models.filter import Filter
from api.models.segment import Segment
from api.tools.audio import silence_if_no_audio
from api.tools.enums import SupportedGames
from api.tools.ffmpeg import merge_videos

logger = logging.getLogger("uvicorn")
valorant_mask = Image.open(VALORANT_MASK_PATH)
csgo2_mask = Image.open(CSGO2_MASK_PATH)


class Box:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        shift_x: int,
        stretch: bool,
        from_center: bool = True,
    ) -> None:
        """
        :param x: Offset in pixels from the left of the video or from the center if use_offset is enabled
        :param y: Offset in pixels from the top of the video
        :param width: Width of the box in pixels
        :param height: Height of the box in pixels
        :param shift_x: Shift the box by a certain amount of pixels to the right
        :param stretch: Stretch the box to fit the video
        :param use_offset: If enabled, x will be from the center of the video, else it will be from the left (usef)

        example:
        If you want to create a box at 50 px from the center on x, but shifted by 20px to the right
        you would do:
        Box(50, 0, 100, 100, 20)
        """
        if from_center:
            half = 720 if stretch else 960
            self.x = half - x + shift_x
        else:
            self.x = x + shift_x

        self.y = y
        self.width = width
        self.height = height

    def __iter__(self) -> Any:
        yield self.x
        yield self.y
        yield self.width
        yield self.height


class Highlight(Thingy):
    segments_path: Optional[str]
    local_filters: Optional[Dict[str, Any]]

    @property
    def name(self) -> str:
        return str(os.path.splitext(os.path.basename(self.path))[0])

    async def extract_thumbnails(self) -> bool:
        """
        Extract the first image of a highlight
        """
        thumbnail_path = os.path.join(self.directory, "thumbnail.jpg")
        ffmpeg.input(self.path).filter("scale", 640, -1).output(
            thumbnail_path, vframes=1
        ).overwrite_output().run(quiet=True)

        thumbnail_path_full_size = os.path.join(
            self.directory, "thumbnail_full_size.jpg"
        )
        ffmpeg.input(self.path).output(
            thumbnail_path_full_size, vframes=1
        ).overwrite_output().run(quiet=True)

        self.update(
            {
                "thumbnail_path": thumbnail_path,
                "thumbnail_path_full_size": thumbnail_path_full_size,
            }
        )
        self.save()
        return True

    async def extract_images(
        self,
        post_process: Callable,
        coordinates: Box,
        framerate: int = 4,
        save_path: str = "images",
        force_extract: bool = False,
    ) -> bool:
        """
        Extracts images from a video at a given framerate

        :param post_process: Function to apply to each image
        :param coordinates: Coordinates of the box to extract
        :param framerate: Framerate to extract the images
        :param save_path: Path to save the images

        """
        if self.images_path and not force_extract:
            return False
        images_path = os.path.join(self.directory, save_path)

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

        if save_path == "images":
            self.update({"images_path": images_path})
            self.save()

        return True

    async def extract_overwatch_images(
        self, framerate: int = 4, stretch: bool = False
    ) -> bool:
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

            im = ImageOps.grayscale(Image.merge("RGB", (r, g, b)))

            final = Image.new("RGB", (100, 100))
            final.paste(im, (0, 0))
            return final

        return await self.extract_images(
            post_process, Box(50, 490, 100, 100, 0, stretch), framerate=framerate
        )

    async def extract_valorant_images(
        self, framerate: int = 4, stretch: bool = False
    ) -> bool:
        def _apply_filter_and_do_operations(
            image: Image, image_filter: ImageFilter
        ) -> Image:
            image = image.filter(image_filter)

            image = image.crop((1, 1, image.width - 2, image.height - 2))

            image.paste(valorant_mask, (0, 0), valorant_mask)

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
            post_process, Box(61, 801, 122, 62, 0, stretch), framerate=framerate
        )

    async def extract_csgo2_images(
        self, framerate: int = 4, stretch: bool = False
    ) -> bool:
        def post_process(image: Image) -> Image:
            image = ImageOps.grayscale(
                image.filter(ImageFilter.FIND_EDGES).filter(
                    ImageFilter.EDGE_ENHANCE_MORE
                )
            )
            final = Image.new("RGB", (100, 100))
            final.paste(image, (0, 0))
            final.paste(csgo2_mask, (0, 0), csgo2_mask)
            return final

        return await self.extract_images(
            post_process, Box(50, 925, 100, 100, 20, stretch), framerate=framerate
        )

    async def extract_the_finals_images(
        self, framerate: int = 4, stretch: bool = False
    ) -> bool:
        def is_color_close(
            pixel: Tuple[int, int, int],
            expected: Tuple[int, int, int],
            threshold: int = 100,
        ) -> bool:
            distance: int = (
                sum((pixel[i] - expected[i]) ** 2 for i in range(len(pixel))) ** 0.5
            )
            return distance < threshold

        def post_process_killfeed(image: Image) -> Image:
            r, g, b = image.split()
            for x in range(image.width):
                for y in range(image.height):
                    if not is_color_close(
                        (r.getpixel((x, y)), g.getpixel((x, y)), b.getpixel((x, y))),
                        (12, 145, 201),
                        120,
                    ):
                        r.putpixel((x, y), 0)
                        b.putpixel((x, y), 0)
                        g.putpixel((x, y), 0)

            im = ImageOps.grayscale(Image.merge("RGB", (r, g, b)))

            final = Image.new("RGB", (250, 115))
            final.paste(im, (0, 0))
            return final

        killfeed_state = await self.extract_images(
            post_process_killfeed,
            Box(1500, 75, 250, 115, 0, stretch, from_center=False),
            framerate=framerate,
        )

        def post_process(image: Image) -> Image:
            r, g, b = image.split()
            for x in range(image.width):
                for y in range(image.height):
                    if not is_color_close(
                        (r.getpixel((x, y)), g.getpixel((x, y)), b.getpixel((x, y))),
                        (255, 255, 255),
                    ):
                        r.putpixel((x, y), 0)
                        b.putpixel((x, y), 0)
                        g.putpixel((x, y), 0)

            im = ImageOps.grayscale(Image.merge("RGB", (r, g, b)))

            final = Image.new("RGB", (200, 120))
            final.paste(im, (0, 0))
            return final

        return (
            await self.extract_images(
                post_process,
                Box(20, 800, 200, 120, 0, stretch, from_center=False),
                framerate=framerate,
                save_path="usernames",
                force_extract=True,
            )
            and killfeed_state
        )

    async def extract_images_from_game(
        self, game: SupportedGames, framerate: int = 4, stretch: bool = False
    ) -> bool:
        if game == SupportedGames.OVERWATCH:
            return await self.extract_overwatch_images(framerate, stretch)
        elif game == SupportedGames.VALORANT:
            return await self.extract_valorant_images(framerate, stretch)
        elif game == SupportedGames.CSGO2:
            return await self.extract_csgo2_images(framerate, stretch)
        elif game == SupportedGames.THEFINALS:
            return await self.extract_the_finals_images(framerate, stretch)
        else:
            raise NotImplementedError(f"game {game} not supported")

    def recompile(self) -> bool:
        from api.tools.utils import sanitize_dict

        global_filters: Dict[str, Any] = {}
        if _global_filters := Filter.find_one({"global": True}):
            global_filters = sanitize_dict(_global_filters.filters or {})

        highlight_filters: Dict[str, Any] = {}
        if _highlight_filters := Filter.find_one({"highlight_id": self.id}):
            highlight_filters = sanitize_dict(_highlight_filters.filters or {})

        filters = {
            **global_filters,
            **highlight_filters,
        }

        result = sanitize_dict(self.local_filters) != filters
        self.local_filters = filters
        self.save()
        return result

    async def extract_segments(
        self, timestamps: List[Tuple[float, float]], stretch: bool = False
    ) -> List[Segment]:
        """
        Segment a video into multiple videos

        :param timestamps: List of tuples containing the start
            and end of the segment in seconds

        :return: List of paths to the segmented videos
        """
        if not self.local_filters:
            self.local_filters = {}
            self.save()

        if not self.segments_path:
            self.segments_path = os.path.join(self.directory, "segments")

        if not os.path.exists(self.segments_path):
            os.mkdir(self.segments_path)

        old_segments = Segment.find({"highlight_id": self.id}).to_list(None)

        recompile = self.recompile()
        if recompile:
            Segment.delete_many({"highlight_id": self.id})

        # Make a list of timestamps that are new, not in the database
        new_timestamps = []
        for start, end in timestamps:
            if (
                not any(
                    old_segment.start == start and old_segment.end == end
                    for old_segment in old_segments
                )
                or recompile
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
                if old_segment.downscaled_path:
                    os.remove(old_segment.downscaled_path)
                Segment.delete_one({"_id": old_segment.id})
            else:
                segments.append(old_segment)

        video = ffmpeg.input(self.path)
        audio = silence_if_no_audio(video.audio, self.path)

        for (start, end) in new_timestamps:
            segment_save_path = os.path.join(self.segments_path, f"{start}-{end}.mp4")
            dar = 4 / 3 if stretch else 16 / 9
            (
                ffmpeg.input(
                    self.path,
                )
                .apply_filters(self.id)
                .filter("setdar", dar)
                .output(audio, segment_save_path, ss=f"{start}", to=f"{end}")
                .overwrite_output()
                .run(quiet=True)
            )
            segment = Segment(
                {
                    "highlight_id": self.id,
                    "path": segment_save_path,
                    "start": start,
                    "end": end,
                    "enabled": True,
                }
            )
            segment.save()
            segments.append(segment)

        return segments

    async def concatenate_segments(self) -> bool:
        """
        Concatenate all the segments of a highlight into a single video
        """

        segments = (
            Segment.find({"highlight_id": self.id, "enabled": True})
            .sort("start")
            .to_list(None)
        )

        if not segments:
            self.merge_path = None
            self.save()
            return False

        self.merge_path = os.path.join(self.directory, "merged.mp4")
        self.save()

        await merge_videos(
            [segment.path for segment in segments], self.merge_path, False
        )

        return True

    async def scale_video(
        self,
        width: int = 1920,
        height: int = 1080,
        backup: str = BACKUP,
        stretch: bool = False,
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
            f"WARNING:Scaling video {self.path}, saving a backup in ./backup"
        )

        if not os.path.exists(backup):
            os.makedirs(backup)

        backup_path = os.path.join(backup, os.path.basename(self.path))
        shutil.move(self.path, backup_path)

        video = ffmpeg.input(backup_path)
        audio = silence_if_no_audio(video.audio, backup_path)

        video = video.filter("scale", w=width, h=height)
        video = (
            video.filter("setdar", 4 / 3) if stretch else video.filter("setdar", 16 / 9)
        )

        ffmpeg.output(video, audio, self.path, start_number=0).run(quiet=True)

    async def remove(self) -> None:
        """
        Delete the video and all its segments
        """
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)

        Segment.delete_many({"highlight_id": self.id})
        Filter.delete_one({"highlight_id": self.id})
        self.delete()

    async def extract_snippet_in_lower_resolution(self, stretch: bool = False) -> bool:
        """Extract 5 seconds of a highlight in lower resolution"""
        if self.snippet_path:
            return False

        snippet_path = os.path.join(self.directory, "snippet.mp4")

        video = ffmpeg.input(self.path, sseof="-20")
        audio = silence_if_no_audio(video.audio, self.path)

        video = video.filter("scale", 640, -1)
        video = (
            video.filter("setdar", 4 / 3) if stretch else video.filter("setdar", 16 / 9)
        )
        ffmpeg.output(video, audio, snippet_path, t="00:00:5").run(quiet=True)

        self.update({"snippet_path": snippet_path})
        self.save()

        return True


Highlight.add_view("defaults", include=("_id", "name", "index", "enabled"))
