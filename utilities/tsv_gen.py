#import glob
import copy
import time
#from pathlib import Path
from loguru import logger
import pandas as pd
import numpy as np
from collections import defaultdict
#from openpyxl import load_workbook
#from openpyxl.utils.dataframe import dataframe_to_rows
from .gdrive import TemplateFolder, Colors
from .gcs import gcs_list_prefixes, GCSFileCacheManager
from .ai_gen import AiProductGenerator, AiDesignGenerator
from .constants import *
from .retries import retry_with_exponential_backoff
#from tempfile import NamedTemporaryFile


class AmazonGenerator:
    template_folder = TemplateFolder()

    def __init__(
        self,
        brand,
        client,
        bucket,
        template_id,
        clothes_type: str,
        kids: bool = False,
        dont_use_caching: bool = False,
    ) -> None:
        self.brand = brand
        self.gcs_client = client
        self.bucket = bucket
        self.template_id = template_id
        self.clothes_type = clothes_type
        self.kids = kids
        self.cache_file_man = GCSFileCacheManager(CSV_CACHE_BUCKET)
        self.dont_use_caching = dont_use_caching

    def create_parent_sku(self, product_name):
        kids_suffix = "-yth" if self.kids else ""
        clothes_suffix = CLOTHES_SUFFIX[self.clothes_type]
        parent_product_sku = (
            product_name.replace(" ", "-")[:MAX_NAME_SKU_LENGTH]
            + clothes_suffix
            + kids_suffix
        )
        return parent_product_sku

    def generate_amazon_listing(
        self,
        imgs: list,
        product_name: str,
        subfolder: str,
        product_title: str = None,
        product_description: str = None,
        keyphrases: list = None,
        bullets: list = None,
        base_price: float = None,
        additional_large_size: float = None,
        new_file: bool = False,
    ) -> str:
        """Generate an amazon listing from a template file.
        Args:
            template_file (Path): Path to the template file.
            imgs_folder (list): list of images to upload.
        Returns:
            str: tempfile name
        """
        # Read the template file
        self.template_file = self.template_folder.download_template(
            self.template_id
        )
        self.subfolder = subfolder
        df = pd.read_excel(
            self.template_file, sheet_name="Template", header=None
        )
        first_2_rows = df.loc[:2, :]  # Save intro rows to re-add later on

        # Since pandas 2.1.0 the next commented code line produced columns with
        # float64 dtype instead of object. This raised a FutureWarning when
        # assigning str values to df. Solved (not cleanly) with next 4 lines.
        # df = pd.read_excel(self.template_file, sheet_name="Template", skiprows=2)
        df = df.drop([0, 1])
        df.columns = df.iloc[0].values
        df = df.drop(2)
        df.reset_index(drop=True, inplace=True)
        original_dtypes = df.dtypes

        # Get required fields
        fields = (
            pd.read_excel(
                self.template_file, sheet_name="Data Definitions", skiprows=1
            )
            .ffill()  # .fillna(method="ffill") deprecated since pandas 2.1.0
            .drop(0)
        )
        field_mapper = (
            fields[["Field name", "Local label name"]]
            .set_index("Field name")["Local label name"]
            .to_dict()
        )
        required_fields = fields[fields["Required?"] == "Required"][
            "Field name"
        ]
        # Get the valid values
        valid_values = (
            pd.read_excel(
                self.template_file,
                sheet_name="Valid Values",
                skiprows=1,
                header=None,
            )
            .set_index(1)
            .drop(0, axis=1)
            .astype(str)
        )
        valid_values = valid_values.apply(
            lambda x: x.dropna().unique().tolist(), axis=1
        )
        valid_values.index = valid_values.index.str.replace(
            r" - .*", "", regex=True
        )
        valid_values = valid_values[valid_values.str.len() > 0]
        valid_values = valid_values[~valid_values.index.duplicated()]

        # Fill first line with Parent product
        parent_product_sku = self.create_parent_sku(product_name)
        main_img_url = self.to_url(
            product_name,
            next(img.name for img in imgs if "-1-" in img.name.lower()),
        )
        try:
            size_img_url = self.to_url(
                product_name,
                next(
                    img.name for img in imgs if "size guide" in img.name.lower()
                ),
            )
        except StopIteration:
            size_img_url = None
        # Populate parent row
        size_price_offset = {f"{i}XL": additional_large_size for i in [3, 4, 5]}
        df.loc[0, "item_sku"] = parent_product_sku
        df.loc[0, "brand_name"] = (
            self.brand if self.brand in NON_GENERIC_BRANDS else "Generic"
        )
        df.loc[0, "item_name"] = " ".join(
            [
                self.brand,
                product_name.title(),
                PRODUCT_NAME_PHRASE[self.clothes_type],
            ]
        )
        df.loc[0, "main_image_url"] = main_img_url
        df.loc[0, "manufacturer"] = self.brand
        df.loc[0, "parent_child"] = "Parent"
        if product_description:
            df.loc[0, "product_description"] = product_description
        if product_title:
            df.loc[0, "item_name"] = product_title
        if keyphrases:
            df.loc[0, "generic_keywords"] = ", ".join(keyphrases)

            for i, keyphrase in enumerate(keyphrases):
                df.loc[0, f"platinum_keywords{i+1}"] = keyphrase

        if bullets:
            for i, bullet in enumerate(bullets):
                df.loc[0, f"bullet_point{i+1}"] = bullet
        if self.kids:
            df.loc[0, "age_range_description"] = "Kid"

        # Get the images and sort them by color

        color_map = Colors().get_colors()
        color_variants = list(color_map.keys())
        imgs_by_color = defaultdict(list)
        for img in imgs:
            found_color = False
            #for color in COLOR_VARIANTS:
            for color in color_variants:
                aliases = [color]
                if color in COLOR_ALIASES:
                    aliases += COLOR_ALIASES[color]
                if any(c.lower() in img.name.lower() for c in aliases):
                    imgs_by_color[color].append(img.name)
                    found_color = True
            if not found_color and "size guide" not in img.name.lower():
                imgs_by_color["no-color"].append(img.name)

        # Assume the name of the folder is the product name

        new_rows = []
        sizes_to_loop = KIDS_SIZES if self.kids else SIZE_VARIANTS
        for color, imgs in imgs_by_color.copy().items():
            for size in sizes_to_loop:
                copy_imgs = copy.deepcopy(imgs)
                if color == "no-color":
                    continue
                try:
                    main_img = next(
                        img for img in copy_imgs if "-1-" in img.lower()
                    )
                except StopIteration:
                    main_img = copy_imgs[0]
                main_img_url = self.to_url(
                    product_name,
                    main_img,
                )
                copy_imgs.remove(main_img)
                str_size = size if type(size) is str else f"{size[0]}-{size[1]}"
                fields_to_fill = {
                    "item_sku": "-".join(
                        [
                            parent_product_sku,
                            color[: min(len(color), 5)],
                            str_size,
                        ]
                    ),
                    "brand_name": (
                        self.brand
                        if self.brand in NON_GENERIC_BRANDS
                        else "Generic"
                    ),
                    "item_name": (
                        product_title
                        if product_title
                        else " ".join(
                            [
                                self.brand,
                                product_name.title(),
                                PRODUCT_NAME_PHRASE[self.clothes_type],
                            ]
                        )
                    ),
                    #"color_map": COLOR_MAP[color],
                    "color_map": color_map[color],
                    "color_name": color,
                    "size_name": str_size,
                    "size_map": SIZE_MAP.get(str_size, "One Size"),
                    "main_image_url": main_img_url,
                    "manufacturer": self.brand,
                    # "product_description": "DESC", This will be AI autogenerated later on
                    "parent_child": "Child",
                    "parent_sku": parent_product_sku,
                    "list_price_with_tax": base_price
                    + size_price_offset.get(size, 0),
                    "purchasable_offer[marketplace_id=A1F83G8C2ARO7P]#1.our_price#1.schedule#1.value_with_tax": base_price
                    + size_price_offset.get(size, 0),
                }

                if product_description:
                    fields_to_fill["product_description"] = product_description
                if keyphrases:
                    fields_to_fill["generic_keywords"] = ", ".join(keyphrases)
                    for i, keyphrase in enumerate(keyphrases):
                        fields_to_fill[f"platinum_keywords{i+1}"] = keyphrase
                if bullets:
                    for i, bullet in enumerate(bullets):
                        fields_to_fill[f"bullet_point{i+1}"] = bullet
                apparel_or_shirt = (
                    "shirt" if self.clothes_type == "t-shirt" else "apparel"
                )
                if self.kids:
                    fields_to_fill[f"{apparel_or_shirt}_size_class"] = "Age"
                    fields_to_fill["age_range_description"] = "Kid"
                    fields_to_fill[f"{apparel_or_shirt}_size"] = (
                        f"{size[0]} Years"
                    )
                    fields_to_fill[f"{apparel_or_shirt}_size_to"] = (
                        f"{size[1]} Years"
                    )

                else:
                    fields_to_fill[f"{apparel_or_shirt}_size_class"] = "Alpha"
                    fields_to_fill[f"{apparel_or_shirt}_size"] = size

                i = 0
                for i, img in enumerate(copy_imgs):  # Load color images
                    fields_to_fill[f"other_image_url{i+1}"] = self.to_url(
                        product_name, img
                    )
                ii = 0
                for ii, img in enumerate(
                    imgs_by_color["no-color"]
                ):  # Load no-color images
                    if i + ii + 1 >= 8:
                        break
                    fields_to_fill[f"other_image_url{i + ii + 2}"] = (
                        self.to_url(product_name, img)
                    )
                if size_img_url:
                    size_i = min([i + ii + 3, 8])
                    fields_to_fill[f"other_image_url{size_i}"] = (
                        size_img_url  # Add sizes reference last
                    )
                first_row = df.loc[0, :].copy()
                first_row[first_row.index.str.startswith("other_image_url")] = (
                    ""
                )
                first_row.update(fields_to_fill)
                new_rows.append(first_row)
        new_rows_df = pd.DataFrame(new_rows)
        # Since pandas 2.1.0 next commented code line raised a FutureWarning
        # regarding concat of data frames with NAs. Solved in line below.
        # df = pd.concat([df, new_rows_df], ignore_index=True)
        df = pd.concat(
            [df.astype(new_rows_df.dtypes), new_rows_df.astype(df.dtypes)],
            ignore_index=True,
        )
        if new_file:
            with self.cache_file_man.open(self.subfolder, mode="w") as f:
                first_2_rows.to_csv(f, sep="\t", index=False, header=False)
        # clean parent row
        df.loc[0, ~df.columns.isin(PARENT_FIELDS)] = pd.NA
        self.validate_data(df, valid_values, field_mapper, required_fields)
        original_dtypes[original_dtypes == "int64"] = "Int64"
        df = df.astype(original_dtypes[original_dtypes == "Int64"])
        df.astype("object").fillna("", inplace=True)
        with self.cache_file_man.open(self.subfolder) as f:
            df.to_csv(f, sep="\t", index=False, header=False, mode="a")
        return self.cache_file_man.buffer

    def validate_data(self, df, valid_values, field_mapper, required_fields):
        """Validate the data in the dataframe against the fields"""
        for column in df.columns:
            second_row_value = df[column].iloc[1]
            if (
                pd.isna(second_row_value) or second_row_value == ""
            ) and column in required_fields.values:
                logger.warning(
                    f"Required field {field_mapper[column]} is empty"
                )
            if column not in field_mapper:
                continue
            if field_mapper[column] not in valid_values:
                continue
            if (
                not df[column]
                .astype(str)
                .isin(valid_values[field_mapper[column]] + [str(pd.NA)])
                .all()
            ):
                if df[column].isna().all():
                    continue
                raise ValueError(
                    f"Invalid values in column {field_mapper[column]}, values: {df[column].unique()}, valid values: {valid_values[field_mapper[column]]}"
                )

        print("Data validated successfully!")

    def to_url(self, product_name: str, img_name: str) -> str:
        # BASE_URL = "https://d.img.vision/merchpanda/"
        BASE_URL = f"{GOOGLE_STORAGE_URL}/{self.bucket}/{self.subfolder}"
        return f"{BASE_URL}/{product_name}/{img_name}"

    @retry_with_exponential_backoff
    def generate_amazon_listing_from_folder(
        self,
        folder_name: str,
        bulkbar,
        base_price: float = None,
        additional_large_size: float = None,
        base_product_title_phrase: str = None,
        ai_generate_title: bool = False,
        ai_inspect_tshirt: bool = False,
        ai_generate_desc: bool = False,
        ai_generate_bullets: bool = False,
        ai_generate_keywords: bool = False,
    ):
        """Go through bucket subfolders and generate all product listings

        Args:
            folder_name (str): the folder on the GCP bucket
            template_id (str): the id of the template on google drive
            ai_generate_title (bool, optional): Use AI to generate title or stick to default?. Defaults to False.
            ai_generate_desc (bool, optional): _description_. Defaults to False.
            ai_generate_bullets (bool, optional): _description_. Defaults to False.
            ai_generate_keywords (bool, optional): _description_. Defaults to False.
        """
        self.subfolder = folder_name.replace("/", "")
        subfolders = list(
            gcs_list_prefixes(self.gcs_client, self.bucket, folder_name, "/")
        )
        logger.info(f"Found subfolders: {subfolders} for folder {folder_name}")
        try:
            existing_df = pd.read_csv(
                self.cache_file_man.open(self.subfolder, mode="r"),
                sep="\t",
                skiprows=2,
            )
        except pd.errors.EmptyDataError:
            existing_df = pd.DataFrame({"item_sku": ["-1"]})

        for i, sub_subfolder in enumerate(subfolders):
            product_name = sub_subfolder.split("/")[-2]
            if (
                any(
                    self.create_parent_sku(product_name)
                    == existing_df["item_sku"]
                )
                and not self.dont_use_caching
            ):
                bulkbar.progress(
                    (i + 1) / len(subfolders),
                    f"Using cache for {sub_subfolder}",
                )
                time.sleep(0.2)
                continue

            imgs = []
            for img in self.gcs_client.list_blobs(
                self.bucket, prefix=sub_subfolder, delimiter="/"
            ):
                img.name = img.name.split("/")[-1]
                imgs.append(img)

            if ai_inspect_tshirt:
                try:
                    flat_img = next(
                        img for img in imgs if "-1-" in img.name.lower()
                    ).name
                except StopIteration:
                    flat_img = imgs[0].name
                tshirt_desctiption = AiProductGenerator.inspect_tshirt(
                    self.to_url(product_name, flat_img)
                )
            else:
                tshirt_desctiption = ""
            ai = AiProductGenerator(
                product_name, tshirt_desctiption, self.clothes_type
            )
            if ai_generate_title:
                product_title = ai.generate_title()
                product_title = f"{self.brand} {product_title}"
            elif base_product_title_phrase:
                product_title = (
                    f"{self.brand} {product_name} {base_product_title_phrase}"
                )
            else:
                product_title = None

            if ai_generate_desc:
                product_description = ai.generate_description()
            else:
                product_description = None

            if ai_generate_keywords:
                keyphrases = ai.generate_keyphrases()
            else:
                keyphrases = None

            if ai_generate_bullets:
                bullets = ai.generate_bullets()
            else:
                bullets = None

            logger.info(f"Product name: {product_name}")
            if i == 0:
                self.generate_amazon_listing(
                    imgs,
                    product_name,
                    subfolder=folder_name.replace("/", ""),
                    product_title=product_title,
                    product_description=product_description,
                    keyphrases=keyphrases,
                    bullets=bullets,
                    base_price=base_price,
                    additional_large_size=additional_large_size,
                    new_file=True,
                )
            else:
                self.generate_amazon_listing(
                    imgs,
                    product_name,
                    subfolder=folder_name.replace("/", ""),
                    product_title=product_title,
                    product_description=product_description,
                    keyphrases=keyphrases,
                    bullets=bullets,
                    base_price=base_price,
                    additional_large_size=additional_large_size,
                )
            bulkbar.progress((i + 1) / len(subfolders), sub_subfolder)
            # callback_update_progress(subfolder)
        bulkbar.progress(1.0, "Done!")
        return self.cache_file_man.buffer

    @retry_with_exponential_backoff
    def generate_plain_product_descriptions(self, folder_name: str, aibar):
        self.subfolder = folder_name.replace("/", "")
        subfolders = list(
            gcs_list_prefixes(self.gcs_client, self.bucket, folder_name, "/")
        )
        logger.info(f"Found subfolders: {subfolders} for folder {folder_name}")
        rows = []
        try:
            with self.cache_file_man.open(
                f"{self.subfolder}-plain-ai", mode="r"
            ) as f:
                existing_df = pd.read_csv(f, sep="\t")
        except pd.errors.EmptyDataError:
            existing_df = pd.DataFrame({"product_name": ["-1"]})

        for i, subfolder in enumerate(subfolders):
            aibar.progress(
                (i + 1) / len(subfolders), f"processing... {subfolder}"
            )
            product_name = subfolder.split("/")[-2]
            if (
                any(existing_df["product_name"] == product_name)
                and not self.dont_use_caching
            ):
                row = (
                    existing_df[existing_df.product_name == product_name]
                    .iloc[0, :]
                    .to_dict()
                )
                rows.append(row)
                time.sleep(0.2)
                continue
            imgs = []
            for img in self.gcs_client.list_blobs(
                self.bucket, prefix=subfolder, delimiter="/"
            ):
                img.name = img.name.split("/")[-1]
                imgs.append(img)
            try:
                flat_img = next(
                    img for img in imgs if "-1-" in img.name.lower()
                ).name
            except StopIteration:
                flat_img = imgs[0].name
            design_desc = AiDesignGenerator.inspect_design(
                self.to_url(product_name, flat_img)
            )

            ai = AiDesignGenerator(product_name, design_desc)
            product_title = ai.generate_title()
            product_title = f"{self.brand} {product_title}"
            product_description = ai.generate_description()
            bullet1, bullet2 = ai.generate_bullets()
            row = {
                "product_name": product_name,
                "product_title": product_title,
                "product_description": product_description,
                "bullets_1": bullet1,
                "bullets_2": bullet2,
            }
            rows.append(row)
            df = pd.DataFrame(rows)
            with self.cache_file_man.open(
                f"{self.subfolder}-plain-ai", mode="w"
            ) as f:
                df.to_csv(f, index=False, sep="\t")
        return self.cache_file_man.buffer
