from typing import Dict, Any
from pydantic import BaseModel


class IRectangle(BaseModel):
    left: int  # min(x)
    top: int  # max(y)
    right: int  # max(x)
    bottom: int  # min(y)
    properties: Dict[str, Any] = {} 


class IndexedRectangle(BaseModel):
    """
    A rectangle wrapper class that also saves its index / rectangle insertion counter in the parent store.
    This is used to keep track of the insertion order of rectangles in the store.
    """
    rectangle: IRectangle
    z_index: int

    def contains(self, x: int, y: int) -> bool:
        """Checks if a point (x, y) is inside this rectangle's bounds."""
        rectangle = self.rectangle
        return rectangle.left <= x < rectangle.right and rectangle.bottom <= y < rectangle.top
