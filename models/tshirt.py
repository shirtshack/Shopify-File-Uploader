from typing import List

from models.colour_option import ColourOption
from models.size import Size
from models.upload_row import UploadRow
from utilities.tshirt import TShirtUtilities


class TShirt(object):

    def __init__(self,
                 name: str,
                 brand_name: str,
                 colour_options: List[ColourOption],
                 output_material_type: str,
                 department: str,
                 origin: str,
                 fabric_type: str,
                 target_gender: str,
                 age_range_description: str,
                 product_description: str,
                 inner_material_type: str,
                 product_care_instructions: str,
                 model_name: str,
                 closure_type: str,
                 manufacturer: str,
                 search_terms: str,
                 pattern_description: str,
                 occasion_description: str,
                 collar_style: str,
                 fitting_style: str,
                 special_features_1: str,
                 special_features_2: str,
                 special_features_3: str,
                 special_features_4: str,
                 special_features_5: str,
                 key_product_features_1: str,
                 key_product_features_2: str,
                 key_product_features_3: str,
                 key_product_features_4: str,
                 key_product_features_5: str,
                 platinum_keywords_1: str,
                 platinum_keywords_2: str,
                 platinum_keywords_3: str,
                 platinum_keywords_4: str,
                 platinum_keywords_5: str,
                 theme: str,
                 product_lifecycle_supply_type: str,
                 pattern: str):
        self.name = name
        self.brand_name = brand_name
        self.product_name = TShirtUtilities.create_product_name_from_name(self.name)
        self.colour_options = colour_options
        self.sizes = self.__get_sizes()
        self.recommended_browse_node = 1731028031
        self.output_material_type = output_material_type
        self.department = department
        self.origin = origin
        self.fabric_type = fabric_type
        self.target_gender = target_gender
        self.age_range_description = age_range_description
        self.shirt_size_system = "UK"
        self.shirt_size_class = "Alpha"
        self.swatch_image_url = None
        self.product_description = product_description
        self.inner_material_type = inner_material_type
        self.product_care_instructions = product_care_instructions
        self.model_name = model_name
        self.closure_type = closure_type
        self.item_type = "T-Shirt"
        self.manufacturer = manufacturer
        self.search_terms = search_terms
        self.pattern_description = pattern_description
        self.occasion_description = occasion_description
        self.collar_style = collar_style
        self.fitting_type = fitting_style
        self.special_features_1 = special_features_1
        self.special_features_2 = special_features_2
        self.special_features_3 = special_features_3
        self.special_features_4 = special_features_4
        self.special_features_5 = special_features_5
        self.key_product_features_1 = key_product_features_1
        self.key_product_features_2 = key_product_features_2
        self.key_product_features_3 = key_product_features_3
        self.key_product_features_4 = key_product_features_4
        self.key_product_features_5 = key_product_features_5
        self.size_modifier = "Standard"
        self.platinum_keywords_1 = platinum_keywords_1
        self.platinum_keywords_2 = platinum_keywords_2
        self.platinum_keywords_3 = platinum_keywords_3
        self.platinum_keywords_4 = platinum_keywords_4
        self.platinum_keywords_5 = platinum_keywords_5
        self.autographed = "No"
        self.item_type_name = "T-Shirt"
        self.occasion_type = "Casual"
        self.material_type = "Cotton"
        self.weave_type = "Knit"
        self.theme = theme
        self.product_lifecycle_supply_type = product_lifecycle_supply_type
        self.pattern = pattern
        self.sleeve_type = "Short Sleeve"
        self.shipping_weight = 190
        self.website_shipping_weight_unit_of_measure = "GR"
        self.item_width_unit_of_measure = "CM"
        self.item_width = 25
        self.item_height = 2
        self.item_shape = "Letter"
        self.item_height_unit_of_measure = "CM"
        self.item_length_unit_of_measure = "CM"
        self.item_length = 30
        self.condition_type = "New"
        self.currency = "GBP"
        self.handling_time = 1

    @staticmethod
    def __get_sizes() -> List[Size]:
        return [Size(name="Small", code="S", price=11.99, quantity=999),
                Size(name="Medium", code="M", price=11.99, quantity=999),
                Size(name="Large", code="L", price=11.99, quantity=999),
                Size(name="X-Large", code="XL", price=11.99, quantity=999),
                Size(name="XX-Large", code="2XL", price=11.99, quantity=999),
                Size(name="XXX-Large", code="3XL", price=12.99, quantity=999),
                Size(name="XXXX-Large", code="4XL", price=12.99, quantity=999),
                Size(name="XXXXX-Large", code="5XL", price=12.99, quantity=999)]

    def create_colour_option(self, colour_option: ColourOption) -> List[UploadRow]:
        output: List[UploadRow] = []
        for size in self.sizes:
            row = UploadRow()
            row.product_id = ""
            row.product_id_type = ""
            row.product_type = "shirt"
            row.seller_sku = f"{self.name}-T-{colour_option.colour}-{size.code}"
            row.brand_name = self.brand_name
            row.product_name = self.product_name
            row.recommended_browse_nodes = self.recommended_browse_node
            row.outer_material_type = self.output_material_type
            row.colour_map = colour_option.colour_map
            row.colour = colour_option.colour
            row.size = size.code
            row.department = self.department
            row.size_map = size.name
            row.country_region_of_origin = self.origin
            row.fabric_type = self.fabric_type
            row.your_price = size.price
            row.quantity = size.quantity
            row.main_image_url = TShirtUtilities.get_image_url(0, colour_option.images)
            row.target_gender = self.target_gender
            row.age_range_description = self.age_range_description
            row.shirt_size_system = self.shirt_size_system
            row.shirt_size_class = self.shirt_size_class
            row.shirt_size_value = size.code
            row.shirt_body_type = "Regular"
            row.shirt_height_type = "Regular"
            row.other_image_url1 = TShirtUtilities.get_image_url(1, colour_option.images)
            row.other_image_url2 = TShirtUtilities.get_image_url(2, colour_option.images)
            row.other_image_url3 = TShirtUtilities.get_image_url(3, colour_option.images)
            row.other_image_url4 = TShirtUtilities.get_image_url(4, colour_option.images)
            row.other_image_url5 = TShirtUtilities.get_image_url(5, colour_option.images)
            row.other_image_url6 = TShirtUtilities.get_image_url(6, colour_option.images)
            row.other_image_url7 = TShirtUtilities.get_image_url(7, colour_option.images)
            row.other_image_url8 = TShirtUtilities.get_image_url(8, colour_option.images)
            row.swatch_image_url = self.swatch_image_url
            row.parentage = "Child"
            row.parent_sku = self.name
            row.relationship_type = "Variation"
            row.variation_theme = "color-size"
            row.package_level = "unit"
            row.product_description = self.product_description
            row.inner_material_type = self.inner_material_type
            row.product_care_instructions = self.product_care_instructions
            row.model_name = self.model_name
            row.closure_type = self.closure_type
            row.item_type = self.item_type
            row.manufacturer = self.manufacturer
            row.search_terms = self.search_terms
            row.pattern_description = self.pattern_description
            row.occasion_description = self.occasion_description
            row.collar_style = self.collar_style
            row.fitting_type = self.fitting_type
            row.special_features1 = self.special_features_1
            row.special_features2 = self.special_features_2
            row.special_features3 = self.special_features_3
            row.special_features4 = self.special_features_4
            row.special_features5 = self.special_features_5
            row.key_product_features1 = self.key_product_features_1
            row.key_product_features2 = self.key_product_features_2
            row.key_product_features3 = self.key_product_features_3
            row.key_product_features4 = self.key_product_features_4
            row.key_product_features5 = self.key_product_features_5
            row.size_modifier = self.size_modifier
            row.platinum_keywords1 = self.platinum_keywords_1
            row.platinum_keywords2 = self.platinum_keywords_2
            row.platinum_keywords3 = self.platinum_keywords_3
            row.platinum_keywords4 = self.platinum_keywords_4
            row.platinum_keywords5 = self.platinum_keywords_5
            row.is_autographed = self.autographed
            row.item_type_name = self.item_type_name
            row.occasion_type1 = self.occasion_type
            row.material_type = self.material_type
            row.weave_type = self.weave_type
            row.theme = self.theme
            row.product_lifecycle_supply_type = self.product_lifecycle_supply_type
            row.pattern = self.pattern
            row.sleeve_type = self.sleeve_type
            row.shipping_weight = self.shipping_weight
            row.website_shipping_weight_unit_of_measure = self.website_shipping_weight_unit_of_measure
            row.item_width_unit_of_measure = self.item_width_unit_of_measure
            row.item_width = self.item_width
            row.item_height = self.item_height
            row.item_shape = self.item_shape
            row.item_height_unit_of_measure = self.item_height_unit_of_measure
            row.item_length_unit_of_measure = self.item_length_unit_of_measure
            row.item_length_description = self.item_length
            row.condition_type = self.condition_type
            row.currency = self.currency
            row.item_length = 30
            row.handling_time = self.handling_time
            output.append(row)
        return output

    def create_parent_row(self) -> UploadRow:
        row = UploadRow()
        row.product_id = ""
        row.product_id_type = ""
        row.product_type = "shirt"
        row.seller_sku = self.name
        row.brand_name = self.brand_name
        row.product_name = self.product_name
        row.colour_map = ""
        row.colour = ""
        row.size = ""
        row.department = ""
        row.recommended_browse_nodes = self.recommended_browse_node
        row.outer_material_type = self.output_material_type
        row.parentage = "Parent"
        row.item_length = 30
        row.variation_theme = "color-size"
        row.inner_material_type = self.inner_material_type
        row.product_care_instructions = self.product_care_instructions
        row.model_name = self.model_name
        row.closure_type = self.closure_type
        row.item_type = self.item_type
        row.manufacturer = self.manufacturer
        row.search_terms = self.search_terms
        row.pattern_description = self.pattern_description
        row.occasion_description = self.occasion_description
        row.collar_style = self.collar_style
        row.fitting_type = self.fitting_type
        row.special_features1 = self.special_features_1
        row.special_features2 = self.special_features_2
        row.special_features3 = self.special_features_3
        row.special_features4 = self.special_features_4
        row.special_features5 = self.special_features_5
        row.key_product_features1 = self.key_product_features_1
        row.key_product_features2 = self.key_product_features_2
        row.key_product_features3 = self.key_product_features_3
        row.key_product_features4 = self.key_product_features_4
        row.key_product_features5 = self.key_product_features_5
        row.size_modifier = self.size_modifier
        row.platinum_keywords1 = self.platinum_keywords_1
        row.platinum_keywords2 = self.platinum_keywords_2
        row.platinum_keywords3 = self.platinum_keywords_3
        row.platinum_keywords4 = self.platinum_keywords_4
        row.platinum_keywords5 = self.platinum_keywords_5
        row.is_autographed = self.autographed
        row.item_type_name = self.item_type_name
        row.occasion_type1 = self.occasion_type
        row.material_type = self.material_type
        row.weave_type = self.weave_type
        row.theme = self.theme
        row.product_lifecycle_supply_type = self.product_lifecycle_supply_type
        row.pattern = self.pattern
        row.sleeve_type = self.sleeve_type
        row.shipping_weight = self.shipping_weight
        row.website_shipping_weight_unit_of_measure = self.website_shipping_weight_unit_of_measure
        row.item_width_unit_of_measure = self.item_width_unit_of_measure
        row.item_width = self.item_width
        row.item_height = self.item_height
        row.item_shape = self.item_shape
        row.item_height_unit_of_measure = self.item_height_unit_of_measure
        row.item_length_unit_of_measure = self.item_length_unit_of_measure
        row.item_length_description = self.item_length
        row.condition_type = self.condition_type
        row.currency = self.currency
        row.handling_time = self.handling_time
        return row

    def create_upload_rows(self) -> List[UploadRow]:
        parent_row = self.create_parent_row()
        colour_options: List[List[UploadRow]] = []
        for colour in self.colour_options:
            colour_options.append(self.create_colour_option(colour))
        output_list = [parent_row]
        output_list.extend([item for sublist in colour_options for item in sublist])
        return output_list
