from typing import Union
from pydantic import BaseModel


class Reorder(BaseModel):
    """DTO for reordering images"""
    name: str


class NoProp(BaseModel):
    """DTO for no value filter"""
    box: bool


class Single(BaseModel):
    """DTO for single value filter"""
    box: bool
    value: Union[float, None]


class Scale(BaseModel):
    """DTO for scale filter"""
    box: bool
    w: Union[float, None]
    h: Union[float, None]


class Filters(BaseModel):
    """DTO for filters"""
    crop: NoProp
    scale: Scale
    blur: Single
    hflip: NoProp
    vflip: NoProp
    saturation: Single
    brightness: Single
    zoom: Single
    grayscale: NoProp
