from typing import Optional

from mongo_thingy import Thingy


class Filter(Thingy):
    filters: Optional[dict]
    pass
