from typing import Union, List

from models.colour_option import ColourOption


class ColourUtilities:

    @staticmethod
    def get_colour_from_file_name(file_name: str) -> Union[str, None]:
        colour_list = ["Black", "Charcoal", "White", "Navy"]
        for colour in colour_list:
            if colour.lower() in file_name.lower():
                return colour
        return None

    @staticmethod
    def create_colour_options(colour: str) -> ColourOption:
        if colour.lower() == "black":
            return ColourOption(colour_map="Black",
                                colour="Black")
        elif colour.lower() == "charcoal":
            return ColourOption(colour_map="Grey",
                                colour="Charcoal")
        elif colour.lower() == "navy":
            return ColourOption(colour_map="Blue",
                                colour="Navy")
        elif colour.lower() == "white":
            return ColourOption(colour_map="White",
                                colour="White")
        else:
            raise NotImplemented(f"{colour} has not been implemented as a colour option")
