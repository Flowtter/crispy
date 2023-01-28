import os

from mongo_thingy import Thingy


class Music(Thingy):
    @property
    def name(self) -> str:
        return str(os.path.splitext(os.path.basename(self.path))[0])


Music.add_view("defaults", include=("_id", "name", "index", "enabled"))
