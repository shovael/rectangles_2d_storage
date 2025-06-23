from __future__ import annotations
from pydantic import BaseModel
from typing import ClassVar

from data_models.rectangle import IRectangle, IndexedRectangle


class QuadNode(BaseModel):
    x1: int  # min(x)
    y1: int  # min(y)
    x2: int  # max(x)
    y2: int  # max(y)
    rectangles: list[IndexedRectangle] = []
    children: list["QuadNode"] | None = None

    CAPACITY: ClassVar[int] = 8
    MIN_SIZE: ClassVar[int] = 1

    def _fits(self, rectangle: IRectangle, x1: int, y1: int, x2: int, y2: int) -> bool:
        return x1 <= rectangle.left and rectangle.right <= x2 and rectangle.bottom <= y1 and y2 <= rectangle.top

    def _subdivide(self):
        """Split this node into four equal children."""
        middle_x = (self.x1 + self.x2) // 2
        middle_y = (self.y1 + self.y2) // 2
        self.children = [
            QuadNode(x1=self.x1, y1=self.y1, x2=middle_x, y2=middle_y),
            QuadNode(x1=middle_x, y1=self.y1, x2=self.x2, y2=middle_y),
            QuadNode(x1=self.x1, y1=middle_y, x2=middle_x, y2=self.y2),
            QuadNode(x1=middle_x, y1=middle_y, x2=self.x2, y2=self.y2)
        ]

    def insert(self, rectangle: IndexedRectangle):
        # 1.  If this is a leaf and still roomy, keep it here.
        if self.children is None:
            width = self.x2 - self.x1
            height = self.y2 - self.y1
            has_room = len(self.rectangles) < self.CAPACITY
            if has_room or (width <= self.MIN_SIZE and height <= self.MIN_SIZE):
                self.rectangles.append(rectangle)
                return
            # Leaf is full → split it, then redistribute existing rects
            self._subdivide()
            old_rects = self.rectangles
            self.rectangles = []
            for old in old_rects:
                self.insert(old)

        # 2. This is now an internal node: see if the rectangle fits in exactly one child
        placed = False
        base_rectangle = rectangle.rectangle
        if self.children:
            for child in self.children:
                if self._fits(base_rectangle, child.x1, child.y1, child.x2, child.y2):
                    child.insert(rectangle)
                    placed = True
                    break
        if not placed:
            self.rectangles.append(rectangle)

    def query(self, x: int, y: int) -> IndexedRectangle | None:
        best: IndexedRectangle | None = None

        # 1. Check rectangles stored at this node
        for rectangle in self.rectangles:
            if rectangle.contains(x, y) and (best is None or best.z_index < rectangle.z_index):
                best = rectangle

        # 2. Descend if possible
        if self.children is not None:
            middle_x = (self.x1 + self.x2) // 2
            middle_y = (self.y1 + self.y2) // 2
            quadrant_index = (middle_y <= y) * 2 + (middle_x <= x)
            child = self.children[quadrant_index]
            deeper_best = child.query(x, y)
            if deeper_best is not None and (best is None or best.z_index < deeper_best.z_index):
                best = deeper_best

        return best


class RectanglesStore(BaseModel):
    bounds: IRectangle | None = None
    _root: QuadNode | None = None
    _next_z: int = 0

    def initialize(self, bounds: IRectangle, rectangles: list[IRectangle]) -> None:
        self.bounds = bounds
        self._root = QuadNode(x1=bounds.left, y1=bounds.bottom, x2=bounds.right, y2=bounds.top)
        for rectangle in rectangles:
            assert RectanglesStore.contains(bounds, rectangle), "Rectangle is not in bounds"  # Optional check, but it's good to be sure.
            indexed_rectangle = IndexedRectangle(rectangle=rectangle, z_index=self._next_z)
            self._next_z += 1
            self._root.insert(indexed_rectangle)

    @classmethod
    def contains(self, border: IRectangle, rectangle: IRectangle) -> bool:
        return (
            border.left <= rectangle.left 
            and rectangle.right <= border.right 
            and border.bottom <= rectangle.bottom 
            and rectangle.top <= border.top
        )


    def find_rectangle_at(self, x: int, y: int) -> IndexedRectangle | None:
        if self._root is None or self.bounds is None:
            raise RuntimeError("Store not initialised")
        return self._root.query(x, y)
