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
            post_process, (899, 801, 122, 62), framerate=framerate
        )

    async def extract_csgo2_images(self, framerate: int = 4) -> bool:
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
            post_process, (930, 925, 100, 100), framerate=framerate
        )

    async def extract_images_from_game(
        self, game: SupportedGames, framerate: int = 4
    ) -> bool:
        if game == SupportedGames.OVERWATCH:
            return await self.extract_overwatch_images(framerate)
        elif game == SupportedGames.VALORANT:
            return await self.extract_valorant_images(framerate)
        elif game == SupportedGames.CSGO2:
            return await self.extract_csgo2_images(framerate)
        else:
            raise NotImplementedError

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
        self, timestamps: List[Tuple[float, float]]
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
            (
                ffmpeg.input(
                    self.path,
                )
                .apply_filters(self.id)
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
            f"WARNING:Scaling video {self.path}, saving a backup in ./backup"
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
        Filter.delete_one({"highlight_id": self.id})
        self.delete()

    async def extract_snippet_in_lower_resolution(self) -> bool:
        """Extract 5 seconds of a highlight in lower resolution"""
        if self.snippet_path:
            return False

        snippet_path = os.path.join(self.directory, "snippet.mp4")

        video = ffmpeg.input(self.path, sseof="-20")
        audio = silence_if_no_audio(video.audio, self.path)
        video = video.filter("scale", 640, -1)
        ffmpeg.output(video, audio, snippet_path, t="00:00:5").run(quiet=True)

        self.update({"snippet_path": snippet_path})
        self.save()

        return True


Highlight.add_view("defaults", include=("_id", "name", "index", "enabled"))
