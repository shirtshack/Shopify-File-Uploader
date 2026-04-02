from typing import List


class ColourOption:

    images: List[str] = []

    def __init__(self,
                 colour_map: str,
                 colour: str):
        self.colour_map = colour_map
        self.colour = colour

