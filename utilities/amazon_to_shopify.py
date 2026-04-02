import os
import io

import pandas as pd
import numpy as np
from loguru import logger

from .gdrive import TemplateFolder, BrandsBuckets
from .gcs import GCSFileCacheManager
from .constants import *


class ShopifyGenerator:

    template_folder = TemplateFolder() # Why outside __init__???

    def __init__(self, brand, manual_brand, template_id, amazon_buffer, subfolder):
        self.brand = brand
        self.manual_brand = manual_brand
        self.template_id = template_id #template_id = '1pUWKsoWhiAop9njrkVU9zmxpf3sqXkNP'
        self.amazon_buffer = amazon_buffer
        self.subfolder = subfolder
        self.cache_file_man = GCSFileCacheManager(CSV_CACHE_BUCKET)


    def convert_amazon_to_shopify(self):
        
        self.template_file = self.template_folder.download_template(
            self.template_id
        )
        self.column_mapping = self.get_column_mapping()

        # Read amazon file and set unique column names
        #amazon_df = pd.read_csv(self.amazon_buffer, header=1) # CSV for standalone testing
        amazon_df = pd.read_csv(self.amazon_buffer, sep="\t", header=1) # TSV for streamlit app
        amazon_df.columns = amazon_df.iloc[0].values
        amazon_df.drop(index=0, inplace=True)
        amazon_df.reset_index(drop=True, inplace=True)

        # Drop rows with no 'Parent SKU'
        no_psku_rows = amazon_df['parent_sku'].isna()
        no_psku_idx = np.where(no_psku_rows)[0]
        if len(no_psku_idx) > 0:
            amazon_df = amazon_df[~no_psku_rows]
            no_psku_idx = no_psku_idx + 4
            logger.warning(
                            f"The following rows in Amazon file have no 'parent_sku' values and were eliminated: {no_psku_idx}"
                        )
        amazon_df.reset_index(drop=True, inplace=True)

        # Add bullet points to product description (to "fluff" it up)
        for i in range(amazon_df.shape[0]):
            for j in range(5): # In the current version, 5 bullet points are generated
                if (
                    pd.notna(amazon_df.loc[i,'product_description']) and
                    pd.notna(amazon_df.loc[i, 'bullet_point'+str(j+1)])
                    ):
                    amazon_df.loc[i,'product_description'] = (
                        amazon_df.loc[i,'product_description']
                        + '\n<p>'
                        + amazon_df.loc[i, 'bullet_point'+str(j+1)]
                        + '</p>'
                        )

        # Filter and rename the necessary columns
        if not set(self.column_mapping.keys()).issubset(amazon_df.columns):
            missing_columns = set(self.column_mapping.keys()) - set(amazon_df.columns)
            # Add logger.warning ???
            raise ValueError(f"Missing columns in Amazon file: {missing_columns}")
        shopify_df = amazon_df[list(self.column_mapping.keys())].rename(columns=self.column_mapping)
        shopify_df.reset_index(drop=True, inplace=True)

        shopify_only_fields = self.get_shopify_only_fields()
        shopify_only_fields = shopify_only_fields.loc[shopify_only_fields.index.repeat(shopify_df.shape[0])]
        shopify_only_fields.reset_index(drop=True, inplace=True)
        shopify_df = pd.concat([shopify_df, shopify_only_fields], axis=1)

        # Drop items with no 'Handle'
        no_handle_rows = shopify_df['Handle'].isna()
        no_handle_idx = np.where(no_handle_rows)[0]
        if len(no_handle_idx) > 0:
            shopify_df = shopify_df[~no_handle_rows]
            no_handle_idx = no_handle_idx + 4
            logger.warning(
                            f"The following rows in Amazon file produced empty 'Handle' values: {no_handle_idx}"
                        )

        # Drop items with no 'Title'
        no_title_rows = shopify_df['Title'].isna()
        no_title_idx = np.where(no_title_rows)[0]
        if len(no_title_idx) > 0:
            shopify_df = shopify_df[~no_title_rows]
            no_title_idx = no_title_idx + 4
            logger.warning(
                            f"The following rows in Amazon file produced empty 'Title' values: {no_title_idx}"
                        )

        shopify_df = self.set_image_urls(amazon_df, shopify_df)

        # Remove brand name from titles
        #brand_name = amazon_df['brand_name'].unique()[0] + ' '
        #brand_name = self.brand + ' '
        brand_name = amazon_df['manufacturer'].unique()[0] + ' '
        shopify_df['Title'] = shopify_df['Title'].str.replace(brand_name, '')

        # Populate Tags field
        field_for_tags = ['Tags',
                        'Option1 Value',
                        'Google Shopping / Age Group',
                        'Google Shopping / Gender',
                        'Handle',
                        ]
        for i in range(shopify_df.shape[0]):
            tags = []
            if pd.notna(amazon_df.loc[i, 'generic_keywords']):
                for keyword in amazon_df.loc[i, 'generic_keywords'].split(', '):
                    tags.append(keyword.replace(' ', '-'))
            for field in field_for_tags:
                tags.append(shopify_df.loc[i, field].replace(' ', '-'))
            shopify_df.loc[i, 'Tags'] = '"' + '","'.join(tags) + '"'

        # Return buffer
        with self.cache_file_man.open(self.subfolder, mode='w') as f:
            shopify_df.to_csv(f, index=False, mode='w')
        return self.cache_file_man.buffer

        ##################### Local Testing #####################
        #shopify_file_path = '../outputs/auto-race-amazon_shopified_2.csv'
        #shopify_df.to_csv(shopify_file_path, index=False)
        #print(f"Processed and saved: {shopify_file_path}")


    def get_column_mapping(self):

        column_mapping = pd.read_excel(self.template_file, sheet_name="mapping")
        column_mapping = dict(column_mapping.values)
        return column_mapping


    def get_shopify_only_fields(self):
        
        field_definitions = pd.read_excel(self.template_file, sheet_name="field_definitions",
                                        skiprows=2)
        field_definitions.drop(columns='Description', inplace=True)
        required_fields = field_definitions[field_definitions['Required']=='required']
        set_fields = field_definitions[field_definitions['Set'].notna()]

        shopify_only_fields = pd.concat([required_fields.set_index('Name'),
                                        set_fields.set_index('Name')])
        for name in self.column_mapping.values():
            if name in shopify_only_fields.index:
                shopify_only_fields.drop(index=name, inplace=True)
        shopify_only_fields = shopify_only_fields.reset_index()
        shopify_only_fields.drop_duplicates(inplace=True)

        shopify_only_fields['Set'] = shopify_only_fields['Set'].fillna(shopify_only_fields['Default'])
        shopify_only_fields.drop(columns='Required', inplace=True)
        shopify_only_fields.drop(columns='Default', inplace=True)
        shopify_only_fields = shopify_only_fields.T
        shopify_only_fields.columns = shopify_only_fields.iloc[0]
        shopify_only_fields.reset_index(drop=True, inplace=True)
        shopify_only_fields.drop(index=0, inplace=True)

        shopify_drop_columns = ['Variant Inventory Qty',
                                'Included / [Primary]',
                                'Included / International',
                                ]
        for column in shopify_drop_columns:
            if column in shopify_only_fields.columns:
                shopify_only_fields.drop(columns=column, inplace=True)

        brands = BrandsBuckets().get_brands_shopify()

        if self.brand in brands.keys():
            shopify_only_fields['Vendor'] = brands[self.brand]

        if self.manual_brand:
            shopify_only_fields['Vendor'] = self.brand

        return shopify_only_fields


    def set_image_urls(self, amazon_df, shopify_df):

        # Specify column names to read from the Amazon file for images
        image_column_names = [
            'main_image_url','other_image_url1', 'other_image_url2',
            'other_image_url3', 'other_image_url4', 'other_image_url5',
            'other_image_url6', 'other_image_url7' , 'other_image_url8'
        ]

        # Initialize the position counter
        image_position_counter = 1

        # Add 'Image Src', 'Image Position', and 'Image Alt Text' columns to the DataFrame
        image_src_col_names = []
        for column_name in image_column_names:
            image_src_col_name = f'Image Src {image_position_counter}'
            image_pos_col_name = f'Image Position {image_position_counter}'
            image_alt_text_col_name = f'Image Alt Text {image_position_counter}'
            
            # Check if the image URL column is empty and then if it contains ".db" or
            # "size-guide". If not, add it to the DataFrame
            if amazon_df[column_name].any():
                if not amazon_df[column_name].str.contains('.db|size-guide').any():
                    shopify_df[image_src_col_name] = amazon_df[column_name]
                    shopify_df[image_pos_col_name] = image_position_counter
                    shopify_df[image_alt_text_col_name] = shopify_df['Option1 Value']
                    image_src_col_names.append(image_src_col_name)
                    image_position_counter += 1

        # Replace empty image URLs with main image URL
        for column_name in image_src_col_names:
            shopify_df[column_name] = shopify_df[column_name].fillna(shopify_df['Variant Image'])

        # Fix spaces in image URLs (replace spaces with %20)
        for column_name in image_src_col_names:
            shopify_df[column_name] = shopify_df[column_name].str.replace(' ', '%20', regex=False)
        if 'Variant Image' in shopify_df.columns:
            shopify_df['Variant Image'] = shopify_df['Variant Image'].str.replace(' ', '%20', regex=False)

        # Rename the temporary columns to their final names
        for i in range(1, image_position_counter):
            shopify_df.rename(columns={
                f'Image Src {i}': 'Image Src',
                f'Image Position {i}': 'Image Position',
                f'Image Alt Text {i}': 'Image Alt Text'
            }, inplace=True)

        return shopify_df
