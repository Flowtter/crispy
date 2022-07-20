from pydantic import BaseModel


class Reorder(BaseModel):
    """DTO for reordering images"""
    name: str
