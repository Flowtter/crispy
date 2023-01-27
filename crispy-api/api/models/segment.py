import os
from typing import Optional

import ffmpeg
from mongo_thingy import Thingy

from api.tools.audio import silence_if_no_audio


class Segment(Thingy):
    filters: Optional[dict]

    @property
    def name(self) -> str:
        return f"{self.start}-{self.end}"

    async def copy_video_in_lower_resolution(self) -> bool:
        if self.downscaled_path:
            return False

        path_no_ext, ext = os.path.splitext(self.path)

        downscaled_path = os.path.join(path_no_ext + "_downscaled" + ext)

        video = ffmpeg.input(self.path)
        audio = silence_if_no_audio(video.audio, self.path)
        video = video.filter("scale", 640, -1)
        ffmpeg.output(
            video,
            audio,
            downscaled_path,
            acodec="aac",
            vcodec="libx264",
        ).overwrite_output().run(quiet=True)

        self.update({"downscaled_path": downscaled_path})
        self.save()

        return True


Segment.add_view("defaults", include=("_id", "highlight_id", "name", "enabled"))
