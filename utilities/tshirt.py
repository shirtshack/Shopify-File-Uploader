from typing import List


class TShirtUtilities:

    @staticmethod
    def create_product_name_from_name(name: str) -> str:
        return name + " T Shirts for Men Uk Funny, Mens T Shirt Funny, Unisex Printed Design Tee Ideal Men's T-Shirt Funny Print, Great Birthday Idea for Men!"

    @staticmethod
    def get_image_url(index: int, image_list: List[str]):
        try:
            item = image_list[index]
            item = item.replace(" ", "_")
            return item
        except IndexError:
            return None
