import random

from data_models.rectangle import IRectangle
from data_models.rectangle_store import RectanglesStore


def add_random_rectangles(count: int) -> list[IRectangle]:
    rectangles = []
    for _ in range(count):
        x1 = random.randint(0, 1000)
        y1 = random.randint(0, 1000)
        x2 = random.randint(x1, 1000) if x1 < 1000 else 1000
        y2 = random.randint(y1, 1000) if y1 < 1000 else 1000
        rectangles.append(IRectangle(left=x1, bottom=y1, right=x2, top=y2))
    return rectangles

if __name__ == "__main__":
    bounds = IRectangle(left=0, bottom=0, right=1000, top=1000)


    rectangles= []
    rectangles.extend(add_random_rectangles(100)) # add 100 random rectangles - nice to have for tests

    # add some rectangles that are not random for specific location testing
    rectangles.append(IRectangle(left=100, bottom=100, right=400, top=400))  
    rectangles.append(IRectangle(left=200, bottom=200, right=300, top=300))

    store = RectanglesStore()
    store.initialize(bounds, rectangles)

    for x, y in [(150, 150), (250, 250), (500, 500)]:
        rectangle = store.find_rectangle_at(x, y)
        print(f"Point {(x,y)} ->", rectangle.rectangle if rectangle else None)