import csv
import os
from typing import Dict, List
import re
import pandas as pd

from collections import OrderedDict

from models.colour_option import ColourOption
from models.tshirt import TShirt
from utilities.colours import ColourUtilities


class FileUtilities:

    @staticmethod
    def get_variation_images_from_folder(folder_path: str) -> List[ColourOption]:
        colour_dict: Dict[str, List[str]] = {}
        for file in os.listdir(folder_path):
            colour = ColourUtilities.get_colour_from_file_name(file)
            if colour in colour_dict.keys():
                colour_dict[colour].append(file)
            else:
                colour_dict[colour] = [file]
        valid_colours = [x for x in colour_dict.keys() if x is not None]
        output: List[ColourOption] = []
        for colour in valid_colours:
            joined_images = colour_dict[colour] + colour_dict[None]
            numbered_images: Dict[int, str] = {}
            for image in joined_images:
                match = re.findall('-\d+-', image)
                if len(match) != 1:
                    raise Exception(f"An exception occurred when trying to find the number for the file {image}")
                number = match[0].strip('-')
                numbered_images[number] = image
            ordered_images = OrderedDict(sorted(numbered_images.items()))
            colour_option = ColourUtilities.create_colour_options(colour)
            ordered_images = list(ordered_images.values())
            url_images = []
            for image in ordered_images:
                url_images.append(FileUtilities.create_image_links_from_file_name(image))
            colour_option.images = url_images
            output.append(colour_option)
        return output

    @staticmethod
    def create_image_links_from_file_name(file_name: str) -> str:
        return f"https://d.img.vision/shirtshack/{file_name}"

    @staticmethod
    def get_product_description() -> str:
        return ("<p>Step into the World of Humour with Printable ShirtShack</p>\
                <p>Become the life of any informal gathering with our unisex ShirtShack's Funny T Shirt. Known as the "
                "dreamland of mens tshirts, we offer a unique blend of comedy and style, making it a good gift for him "
                "or a hilarious present for dad. The customised t shirt design turns the tee into a talking point. "
                "Made for both men and women, it's more than just a t shirt men and women will love, it's a "
                "conversation starter!</p>"
                "\<p>Make them Smile with ShirtShack's Comedy Slogan T Shirt</p>"
                "<p>At ShirtShack, each graphic t shirt is designed to be a showstopper, mainly our funny novelty "
                "t shirt designs that's sure to incite laughter. It's more than mens t-shirts. It's a new way to "
                "express humor and charisma. Our t shirt printing is top-notch, ensuring that the cheeky designs "
                "never fade, even after numerous washes. This funny tshirts for men is the ideal comic relief, "
                "whether it's for a dad's birthday or just a fun weekend.</p>"
                "<p>Elevate Everyday Wear with ShirtShack's Personalised Printed T Shirts</p>"
                "<p>Switch up your everyday style and bring laughter to any occasion with ShirtShack's funny shirts. "
                "With our printed t shirts personalised to suit your sense of humour, we make humor fashionable and fun. "
                "Whether you are looking for spectacular presents for dad or humorous gifts for grandad, these shirts "
                "are a good fit. Our team of exceptional designers ensures each shirt is not just comfortable and "
                "durable, but also a piece that never fails to tickle one’s funny bone. Always be ready for a comedy "
                "show with ShirtShack’s funny shirts - your wardrobe’s favourite humorous companion!</p>"
                "<p>-Unisex design</p>"
                "<p>-Eye-catching printed t-shirt</p>"
                 "<p>-Comfort and style</p>"
                 "<p>-Suitable for any occasion</p><p>-Affordable price</p>")

    @staticmethod
    def create_tshirt_from_folder(folder_path: str) -> TShirt:
        colour_images = FileUtilities.get_variation_images_from_folder(folder_path)
        return TShirt(name=os.path.basename(folder_path),
                      brand_name="ShirtShack",
                      colour_options=colour_images,
                      output_material_type="Cotton",
                      department="Men",
                      origin="United Kingdom",
                      fabric_type="Cotton",
                      target_gender="Male",
                      age_range_description="Adult",
                      product_description=FileUtilities.get_product_description(),
                      inner_material_type="Cotton",
                      product_care_instructions="Machine Wash",
                      model_name=os.path.basename(folder_path),
                      closure_type="Pull On",
                      manufacturer="ShirtShack Clothing",
                      search_terms="Funny unisex t-shirt, Premium cotton fabric, Gift , Unique t-shirt design",
                      pattern_description="Plain",
                      occasion_description="Casual",
                      collar_style="Round Collar",
                      fitting_style="Regular Fit",
                      special_features_1="Ultra Soft RingSpun Cotton Printed T shirt ",
                      special_features_2="Printed T shirt using Eco Friendly waterbased inks in the design",
                      special_features_3="Unisex T Shirt, Relaxed fit",
                      special_features_4="Fast Dispatch, Sending Our Printed Tees Worldwide",
                      special_features_5="Novelty, Funny, Comedy Slogan T-Shirt",
                      key_product_features_1="Great Gifts For Him: Surprise your loved ones with this Funny T Shirt "
                                             "that's sure to bring laughter wherever it's worn. Ideal as a "
                                             "lighthearted grandad gift for him or her or mens birthday present.",
                      key_product_features_2="Personalised T Shirt UK Fashion: This tee isn't just funny, it's "
                                             "custom-made with bold prints that humorously stand out. Represent your "
                                             "personality with our personalised novelty t-shirts and be the life of "
                                             "the party",
                      key_product_features_3="For All the Funny Men Out There: Tired of traditional men's clothing? "
                                             "Our Funny T Shirt is the new cool! It makes a brilliant gift, especially "
                                             "for those wanting to show off their quirky side",
                      key_product_features_4="Unique Presents for Men: Looking for something different from the usual "
                                             "mens tshirts UK has to offer? Why not consider our Funny T Shirt? It's a "
                                             "gift that'll uniquely make them smile every time they wear it",
                      key_product_features_5="Quality Custom T Shirt: Crafted from quality, soft, and durable material, "
                                             "this unisex printed t-shirt is not just funny, it is also comfortable to "
                                             "wear. Great for daily wear or special occasions",
                      platinum_keywords_1="Fun printed t shirt",
                      platinum_keywords_2="Clever pun t-shirt",
                      platinum_keywords_3="Soft, comfortable fabric",
                      platinum_keywords_4="exclusive design",
                      platinum_keywords_5="Funny unisex t-shirt",
                      theme="Comedy",
                      product_lifecycle_supply_type="Fashion",
                      pattern="Solid")

    @staticmethod
    def create_output_dataframe(folder_path) -> pd.DataFrame:
        tshirt = FileUtilities.create_tshirt_from_folder(folder_path)
        outputs = [x.to_dict() for x in tshirt.create_upload_rows()]
        dataframe = pd.DataFrame(outputs)
        return dataframe

    @staticmethod
    def replace_words_in_csv(csv_file_path: str, words_dict: Dict[str, List[str]]):
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csv_file:
            file_content = csv_file.read()
        for key, value in words_dict.items():
            for old_word in value:
                file_content = file_content.replace(old_word, key)
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_file.write(file_content)

    @staticmethod
    def add_header_rows(csv_file_path: str) -> None:
        row_1 = "TemplateType=fptcustom,Version=2023.0608,TemplateSignature=U0hJUlQ=,settings=attributeRow=3&contentLanguageTag=en_GB&dataRow=4&feedType=113&headerLanguageTag=en_GB&isEdit=false&isExpose=false&isProcessingSummary=false&labelRow=2&metadataVersion=MatprodVkxBUHJvZC0xMTQ0&primaryMarketplaceId=amzn1.mp.o.A1F83G8C2ARO7P&ptds=U0hJUlQ%3D&reportProvenance=false&templateIdentifier=1cca5414-68da-4b24-9e20-771c0b766b2e&timestamp=2023-06-08T14%3A19%3A03.692Z, The top three rows are for Amazon.com use only. Do not modify or delete the top three rows.,,,,,,,,,,,,,,,,,,,,,,,,,,Images,,,,,,,,,Variation,,,,,,,Basic,,,,,,,,,,,,,,,,Discovery,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Product Enrichment,,,Dimensions,,,,,,,,,,,,,Compliance,,,,,,,,,,,,,,,,,,,,,,,,,,,Offer,,,,,,,,,,,,,,,,,,,,,,,,,,,,b2b,,,,,,,,,,,,,,,,,,,,,".split(",")
        row_3 = [
            "feed_product_type", "item_sku", "brand_name", "external_product_id", "external_product_id_type",
            "item_name", "recommended_browse_nodes", "outer_material_type", "color_map", "color_name",
            "size_name", "department_name", "size_map", "country_of_origin", "fabric_type", "standard_price",
            "quantity", "main_image_url", "target_gender", "age_range_description", "shirt_size_system",
            "shirt_size_class", "shirt_size", "shirt_size_to", "shirt_neck_size", "shirt_neck_size_to",
            "shirt_sleeve_length", "shirt_sleeve_length_to", "shirt_body_type", "shirt_height_type",
            "other_image_url1", "other_image_url2", "other_image_url3", "other_image_url4", "other_image_url5",
            "other_image_url6", "other_image_url7", "other_image_url8", "swatch_image_url", "parent_child",
            "parent_sku", "relationship_type", "variation_theme", "package_level", "package_contains_quantity",
            "package_contains_identifier", "update_delete", "product_description", "inner_material_type",
            "care_instructions", "model_name", "model", "closure_type", "part_number", "item_type", "manufacturer",
            "gtin_exemption_reason", "language_value1", "language_value2", "language_value3", "language_value4",
            "language_value5", "generic_keywords", "collection_name", "pattern_type", "lifestyle", "style_name",
            "collar_style", "fit_type", "special_features1", "special_features2", "special_features3",
            "special_features4", "special_features5", "bullet_point1", "bullet_point2", "bullet_point3",
            "bullet_point4", "bullet_point5", "special_size_type", "platinum_keywords1", "platinum_keywords2",
            "platinum_keywords3", "platinum_keywords4", "platinum_keywords5", "is_autographed", "item_type_name",
            "occasion_type1", "occasion_type2", "occasion_type3", "occasion_type4", "occasion_type5",
            "sport_type1", "sport_type2", "seasons", "athlete", "team_name", "material_type",
            "fur_description", "weave_type", "theme", "league_name", "shaft_style_type", "lifecycle_supply_type",
            "pattern_name", "item_booking_date", "sleeve_type", "subject_character", "flash_point_unit_of_measure",
            "neck_size", "neck_size_unit_of_measure", "item_length_description", "cup_size",
            "website_shipping_weight", "website_shipping_weight_unit_of_measure", "item_width_unit_of_measure",
            "item_width", "item_height", "item_shape", "item_height_unit_of_measure", "item_length_unit_of_measure",
            "item_length", "legal_disclaimer_description", "safety_warning", "eu_toys_safety_directive_age_warning",
            "eu_toys_safety_directive_warning", "eu_toys_safety_directive_language", "batteries_required",
            "are_batteries_included", "battery_type1", "battery_type2", "battery_type3", "number_of_batteries1",
            "number_of_batteries2", "number_of_batteries3", "number_of_lithium_metal_cells",
            "number_of_lithium_ion_cells",
            "lithium_battery_packaging", "lithium_battery_energy_content",
            "lithium_battery_energy_content_unit_of_measure",
            "lithium_battery_weight", "lithium_battery_weight_unit_of_measure", "item_weight",
            "item_weight_unit_of_measure", "item_volume", "item_volume_unit_of_measure",
            "supplier_declared_material_regulation1", "supplier_declared_material_regulation2",
            "supplier_declared_material_regulation3", "condition_type", "condition_note", "currency",
            "fulfillment_latency", "sale_price", "sale_from_date", "sale_end_date", "max_aggregate_ship_quantity",
            "item_package_quantity", "number_of_items", "offering_can_be_gift_messaged", "offering_can_be_giftwrapped",
            "is_discontinued_by_manufacturer", "product_site_launch_date", "restock_date", "map_price",
            "list_price_with_tax", "merchant_release_date", "list_price", "offering_end_date",
            "max_order_quantity", "merchant_shipping_group_name", "offering_start_date", "liquidate_remainder",
            "delivery_schedule_group_id", "uvp_list_price", "product_tax_code", "minimum_order_quantity_minimum",
            "business_price", "quantity_price_type", "quantity_lower_bound1", "quantity_price1",
            "quantity_lower_bound2", "quantity_price2", "quantity_lower_bound3", "quantity_price3",
            "quantity_lower_bound4", "quantity_price4", "quantity_lower_bound5", "quantity_price5",
            "progressive_discount_type", "progressive_discount_lower_bound1", "progressive_discount_value1",
            "progressive_discount_lower_bound2", "progressive_discount_value2", "progressive_discount_lower_bound3",
            "progressive_discount_value3", "national_stock_number", "unspsc_code", "pricing_action"
        ]
        existing_data = []
        with open(csv_file_path, "r", newline="") as file:
            reader = csv.reader(file, delimiter="\t")  # Change delimiter if needed
            for row in reader:
                existing_data.append(row)
        existing_data.insert(0, row_1)
        existing_data.insert(2, row_3)
        with open(csv_file_path, "w", newline="") as file:
            writer = csv.writer(file, delimiter="\t")  # Change delimiter if needed
            writer.writerows(existing_data)

    @staticmethod
    def reformat_output_file(file_path: str) -> None:
        FileUtilities.replace_words_in_csv(file_path,
                                           {"Language": ["Language1", "Language2", "Language3", "Language4","Language5"],
                                            "Special Features": ["Special Features1", "Special Features2",
                                                                 "Special Features3", "Special Features4", "Special Features5"],
                                            "Key Product Features": ["Key Product Features1", "Key Product Features2",
                                                                     "Key Product Features3", "Key Product Features4",
                                                                     "Key Product Features5"],
                                            "platinum-keywords1 - platinum-keywords5": ["Platinum-keywords1", "Platinum-keywords2",
                                                                                        "Platinum-keywords3", "Platinum-keywords4",
                                                                                        "Platinum-keywords5"],
                                            "Occasion Type": ["Occasion Type1", "Occasion Type2",
                                                              "Occasion Type3", "Occasion Type4",
                                                              "Occasion Type5"],
                                            "Sport Type": ["Sport Type1", "Sport Type2"],
                                            "Battery type/size": ["Battery type/size 1", "Battery type/size 2",
                                                                  "Battery type/size 3"],
                                            "Number of batteries": ["Number of batteries 1", "Number of batteries 2",
                                                                    "Number of batteries 3"],
                                            "Material/Fabric Regulations": ["Material/Fabric Regulations 1", "Material/Fabric Regulations 2",
                                                                            "Material/Fabric Regulations 3"],
                                            "size-modifier": ["Size Modifier"],
                                            "flash_point_unit_of_measure": ["Flash Point Unit Of Measure"],
                                            "Fabric type": ["Fabric Type"],
                                            "Bra cup size": ["Bra Cup Size"],
                                            "Neck size": ["Neck Size"],
                                            "Neck Size unit": ["Neck size Unit"],
                                            "Neck Size Value": ["Neck size Value"],
                                            "Neck Size To Value": ["Neck size To Value"],
                                            "Item Length": ["Item Length Description"]
                                            })
        FileUtilities.add_header_rows(file_path)

    @staticmethod
    def create_single_image_output_file(folder_path: str) -> None:
        tshirt = FileUtilities.create_output_dataframe(folder_path)
        output_name = os.path.basename(folder_path).strip() + "-output.tsv"
        output_path = os.path.join(os.path.dirname(folder_path), output_name)
        tshirt.to_csv(output_path, sep="\t", index=False)
        FileUtilities.reformat_output_file(output_path)

    @staticmethod
    def create_multiple_images_output_file(folder_paths: List[str], output_path: str) -> None:
        dataframes: List[pd.DataFrame] = []
        for folder_path in folder_paths:
            dataframes.append(FileUtilities.create_output_dataframe(folder_path))
        dataframe = pd.concat(dataframes, ignore_index=True)
        dataframe.to_csv(output_path, sep="\t", index=False)
        FileUtilities.reformat_output_file(output_path)

    @staticmethod
    def run_for_parent_folder(parent_folder: str) -> None:
        folder_paths: List[str] = []
        for item in os.listdir(parent_folder):
            item_path = os.path.join(parent_folder, item)
            if os.path.isdir(item_path):
                folder_paths.append(item_path)
        output_name = os.path.basename(parent_folder).strip() + "-output.tsv"
        output_path = os.path.join(os.path.dirname(parent_folder), output_name)
        if len(folder_paths) > 0:
            FileUtilities.create_multiple_images_output_file(folder_paths, output_path)
        else:
            FileUtilities.create_single_image_output_file(parent_folder)

