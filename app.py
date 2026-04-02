import os
import datetime
import pandas as pd
import numpy as np
import hmac

import streamlit as st
import streamlit_ext as ste
import extra_streamlit_components as stx

from PIL import Image
from itertools import cycle
#from zipfile import ZipFile
from utilities.gdrive import TemplateFolder, BrandsBuckets
from utilities.ai_gen import AiProductGenerator
from utilities.tsv_gen import AmazonGenerator
from utilities.amazon_to_shopify import ShopifyGenerator
from utilities.gcs import gcs_list_prefixes
#from tempfile import NamedTemporaryFile
from loguru import logger
from google.cloud import storage
from utilities.constants import *


#### Streamlit app password protection
# (Step 3 in https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso)

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        #if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
        if hmac.compare_digest(st.session_state["password"], os.getenv("ST_PASS")):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        cookie_manager.set(auth_cookie, 'True') # Added for cookie support. Expires in a day by default
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


#if not check_password():
#    st.stop()  # Do not continue if check_password is not True.

#@st.cache_resource
#def get_manager():
#    return stx.CookieManager()

# Workaround for st CachedWidgetWarning (https://github.com/Mohamed-512/Extra-Streamlit-Components/issues/70)
with st.empty():
    @st.cache_resource
    def get_manager():
        return stx.CookieManager()
    cookie_manager = get_manager()

# Code block added for cookie support (extra_streamlit_components)
#cookie_manager = get_manager()
auth_cookie = 'st_auth'
#cookie_manager.set(auth_cookie, 'False')

if 'password' not in st.session_state:
    st.session_state['password'] = ''
auth_cookie_val = cookie_manager.get(cookie=auth_cookie)
if not auth_cookie_val:
    if not check_password():
        st.stop()  # Do not continue if check_password is not True.

#cookie_manager.delete(auth_cookie)

#### Main Streamlit app starts here

subfolder = "ui-tool"

tf = TemplateFolder()

if (  # Lock UI if TSV generation has been triggered
    st.session_state.get("single_gen_but", False)
    or st.session_state.get("bulk_gen_but", False)
    or st.session_state.get("generic_gen_but", False)
) and st.session_state.get("disabled", False) == False:
    st.session_state.disabled = True


def update_title():
    if "product_name" in st.session_state:
        if "t-shirt" in st.session_state["template"].lower():
            clothes_type = "t-shirt"
        elif "hoodie" in st.session_state["template"].lower():
            clothes_type = "hoodie"
        elif "sweatshirt" in st.session_state["template"].lower():
            clothes_type = "sweatshirt"
        else:
            clothes_type = "t-shirt"
        if not st.session_state.get("disable_title_phrase_change", False):
            st.session_state[
                "default_title"
            ] = f"{brand} {st.session_state['product_name'].title()} {PRODUCT_NAME_PHRASE[clothes_type]}"


##### GENERAL OPTIONS FOR BOTH SINGLE PRODUCT OR BULK

st.title("Product List File Generator")
template_list = tf.get_template_list()
template = st.selectbox(
    "Select your template",
    key="template",
    options=[m["name"] for m in template_list],
    disabled=st.session_state.get("disabled", False),
    on_change=update_title,
)

brand_bucket_names = BrandsBuckets().get_brands_buckets()
template_id = next(m["id"] for m in template_list if m["name"] == template)
brand = st.selectbox(
    "Select your brand",
    #BUCKET_NAME.keys(),
    brand_bucket_names.keys(),
    disabled=st.session_state.get("disabled", False),
)

if "t-shirt" in template.lower():
    clothes_type = "t-shirt"
elif "hoodie" in template.lower():
    clothes_type = "hoodie"
elif "sweatshirt" in template.lower():
    clothes_type = "sweatshirt"
else:
    st.write(
        "Couldn't find a clothes type in the template name, please select one below:"
    )
    clothes_type = st.selectbox("Clothes type", ["t-shirt", "hoodie", "sweatshirt"])

is_for_kids = st.checkbox("Kids", disabled=st.session_state.get("disabled", False))

base_price = st.number_input(
    "Base price £",
    value=DEFAULT_PRICE[(is_for_kids, clothes_type)],
    step=1.0,
    disabled=st.session_state.get("disabled", False),
)
additional_large_size = st.number_input(
    "Additional for sizes 3XL and over £",
    value=2.0,
    step=1.0,
    disabled=st.session_state.get("disabled", False),
)
product_name_phrase = st.text_input(
    "Base phrase for title",
    value=PRODUCT_NAME_PHRASE[clothes_type],
    key="product_name_phrase",
    disabled=st.session_state.get("disabled", False),
)
dont_use_caching = st.checkbox(
    "Don't Use Cached results",
    help="If the same folder was processed today (even partially) those results are reused unless this is checked.",
)

client = storage.Client()
#selected_bucket = BUCKET_NAME[brand]
selected_bucket = brand_bucket_names[brand]
bucket = client.get_bucket(selected_bucket)

##### GENERATION FUNCTIONS

# az = AmazonGenerator(
#     brand=brand,
#     client=client,
#     bucket=selected_bucket,
#     template_id=template_id,
#     clothes_type=clothes_type,
#     kids=is_for_kids,
#     dont_use_caching=dont_use_caching,
# )

def gen_title(product_name, tshirt_desc):
    st.session_state["default_title"] = (
        f"{brand} "
        + AiProductGenerator(
            product_name, tshirt_desc, clothing_type=clothes_type
        ).generate_title()
    )


def gen_shirt_desc(files_uploaded, product_name):
    flat_shirt_img_name = [f.name for f in files_uploaded if "-1-" in f.name][0]
    az.subfolder = subfolder
    flat_shirt_url = az.to_url(product_name, flat_shirt_img_name)
    shirt_desc = AiProductGenerator.inspect_tshirt(flat_shirt_url)
    st.session_state["default_tshirt_desc"] = shirt_desc


def gen_product_desc(product_name, tshirt_desc):
    st.session_state["default_desc"] = AiProductGenerator(
        product_name, tshirt_desc, clothing_type=clothes_type
    ).generate_description()


def gen_keywords(product_name, tshirt_desc):
    st.session_state["default_keywords"] = AiProductGenerator(
        product_name, tshirt_desc, clothing_type=clothes_type
    ).generate_keyphrases()


def gen_bullets(product_name, tshirt_desc):
    st.session_state["default_bullets"] = AiProductGenerator(
        product_name, tshirt_desc, clothing_type=clothes_type
    ).generate_bullets()


def upload_images(product_name, files_uploaded):
    for i, file in enumerate(files_uploaded):
        blob = bucket.blob(f"{subfolder}/{product_name}/{file.name}")
        file.seek(0)
        if not blob.exists():
            blob.upload_from_file(file)
        my_bar.progress((i + 1) / len(files_uploaded), text=f"Uploading {file.name}")
    my_bar.progress(1.0, text="Done!")


##### TABS FOR SINGLE PRODUCT OR BULK

tab1, tab2, tab3 = st.tabs(["Bulk generation", "Single product", "AI for designs"])

if "default_keywords" not in st.session_state:
    st.session_state["default_keywords"] = DEFAULT_KEYWORDS
if "default_bullets" not in st.session_state:
    st.session_state["default_bullets"] = DEFAULT_BULLETS

with tab1:
    st.write(
        "IMPORTANT: bulk generation requires that you have previously uploaded the folder structure to Google Cloud Storage."
    )
    folders = gcs_list_prefixes(client, selected_bucket, "", "/")
    folder = st.selectbox(
        "Select your folder:",
        [f for f in folders],
        disabled=st.session_state.get("disabled", False),
    )
    subfolders = [
        x.split("/")[1] for x in gcs_list_prefixes(client, selected_bucket, folder, "/")
    ]
    st.write("Found the following subfolders: ")
    st.markdown(f":orange[{'  ||  '.join(subfolders)}], ")
    
    brand_orig = brand

    brand_change = st.toggle(
        "Change brand name",
        value=True,
        disabled=st.session_state.get("disabled", False),
    )

    manual_brand = False
    if brand_change:
        # Auto-generate default vendor tag based on today's date e.g. 12-mar-t
        today = datetime.date.today()
        default_vendor = f"{today.day}-{today.strftime('%b').lower()}-t"
        brand = st.text_input(
            "Vendor tag (brand name)",
            value=default_vendor,
            disabled=st.session_state.get("disabled", False),
        )
        manual_brand = True
    
    st.write(
        "Select what elements you want AI generated (the more you select the longer it takes to process each product):"
    )

    ai_gen_all = st.toggle(
        "Generate ALL elements using AI",
        value=True,
        disabled=st.session_state.get("disabled", False),
    )
    ai_gen_title = st.toggle(
        "Generate titles using AI",
        value=False,
        disabled=st.session_state.get("disabled", False),
    )
    ai_inspect_tshirt = st.toggle(
        "Inspect clothes using vision AI",
        #value=False,
        value=ai_gen_all,
        disabled=st.session_state.get("disabled", False),
    )
    ai_gen_desc = st.toggle(
        "Generate descriptions using AI",
        #value=False,
        value=ai_gen_all,
        disabled=st.session_state.get("disabled", False),
    )
    ai_gen_bullets = st.toggle(
        "Generate bullets using AI",
        #value=False,
        value=ai_gen_all,
        disabled=st.session_state.get("disabled", False),
    )
    ai_gen_keywords = st.toggle(
        "Generate keywords using AI",
        #value=False,
        value=ai_gen_all,
        disabled=st.session_state.get("disabled", False),
    )

    st.write(
        "Select which list files you want to be generated:"
    )
    amazon_toggle = st.toggle(
        "Amazon",
        value=False,
        disabled=st.session_state.get("disabled", False),
    )
    shopify_toggle = st.toggle(
        "Shopify",
        value=True,
        disabled=st.session_state.get("disabled", False),
    )

    az = AmazonGenerator(
        #brand=brand,
        brand=brand_orig,
        client=client,
        bucket=selected_bucket,
        template_id=template_id,
        clothes_type=clothes_type,
        kids=is_for_kids,
        dont_use_caching=dont_use_caching,
        )

    if st.button("Generate list files from bulk folder", key="bulk_gen_but"):
        # prep data for downloading
        bulk_bar = st.progress(0)
        file_buffer = az.generate_amazon_listing_from_folder(
            folder,
            bulk_bar,
            base_price=base_price,
            additional_large_size=additional_large_size,
            base_product_title_phrase=product_name_phrase,
            ai_generate_title=ai_gen_title,
            ai_inspect_tshirt=ai_inspect_tshirt,
            ai_generate_desc=ai_gen_desc,
            ai_generate_bullets=ai_gen_bullets,
            ai_generate_keywords=ai_gen_keywords,
        )
        st.session_state.disabled = False

        if amazon_toggle:
            file_buffer.seek(0)
            amazon_dl_but = ste.download_button(
                "Download bulk Amazon TSV",
                data=file_buffer.read().encode("utf-8"),
                file_name=f"bulk-products-{folder}.tsv",
                mime="application/octet-stream",
            )

        if shopify_toggle:
            file_buffer.seek(0)
            generator = ShopifyGenerator(
                brand=brand,
                manual_brand=manual_brand,
                template_id='1pUWKsoWhiAop9njrkVU9zmxpf3sqXkNP', # Shopify template id
                amazon_buffer=file_buffer,
                subfolder=subfolder,
                )
            shopify_file_buffer = generator.convert_amazon_to_shopify()
            shopify_file_buffer.seek(0)
            shopify_dl_but = ste.download_button(
                "Download bulk Shopify CSV",
                data=shopify_file_buffer.read().encode("utf-8"),
                file_name=f"bulk-products-shopify-{folder}.csv",
                mime="application/octet-stream",
            )

        if amazon_toggle or shopify_toggle:
            st.write(
                "Note: After downloading the generated file/s, the app needs to be manually refreshed to submit another job."
            )

            if st.button('Refresh app'):
                st.rerun()

with tab2:
    files_uploaded = st.file_uploader("Upload images", accept_multiple_files=True)
    if files_uploaded:
        st.header("Images")
        cols = cycle(
            st.columns(4)
        )
        for file in files_uploaded:
            next(cols).image(Image.open(file), width=150, caption=file.name)
        product_name = files_uploaded[0].name.split("-")[0]
        st.session_state["product_name"] = product_name

        my_bar = st.progress(0)
        st.button(
            "Upload images to GCS",
            on_click=upload_images,
            args=(product_name, files_uploaded),
            disabled=st.session_state.get("disabled", False),
        )
        st.write(f"**Product name:** {product_name}")
        if "default_title" not in st.session_state:
            st.session_state[
                "default_title"
            ] = f"{brand} {product_name.title()} {PRODUCT_NAME_PHRASE[clothes_type]}"
        if "default_tshirt_desc" not in st.session_state:
            st.session_state["default_tshirt_desc"] = ""
        tshirt_desc = st.text_input(
            "What is the t-shirt design?",
            value=st.session_state["default_tshirt_desc"],
            disabled=st.session_state.get("disabled", False),
        )
        st.button(
            "Inspect t-shirt using AI",
            on_click=gen_shirt_desc,
            args=(files_uploaded, product_name),
            disabled=st.session_state.get("disabled", False),
        )
        if "default_desc" not in st.session_state:
            st.session_state["default_desc"] = ""
        product_description = st.text_area(
            "Product description",
            value=st.session_state["default_desc"],
            disabled=st.session_state.get("disabled", False),
        )
        st.button(
            "Generate description using AI",
            on_click=gen_product_desc,
            args=(product_name, tshirt_desc),
            disabled=st.session_state.get("disabled", False),
        )
        product_title = st.text_area(
            "Product title", value=st.session_state["default_title"]
        )
        st.write(f"Title length: {len(product_title)}")
        st.button(
            "Generate title using AI",
            key="ai_gen_title_btn",
            on_click=gen_title,
            args=(product_name, tshirt_desc),
            disabled=st.session_state.get("disabled", False),
        )
        kw_cols = st.columns(5)
        for i, col in enumerate(kw_cols):
            col.text_input(
                f"Keyword {i+1}",
                value=st.session_state["default_keywords"][i],
                disabled=st.session_state.get("disabled", False),
            )
        st.button(
            "Generate keywords using AI",
            on_click=gen_keywords,
            args=(product_name, tshirt_desc),
            disabled=st.session_state.get("disabled", False),
        )

        for i in range(5):
            st.text_input(
                f"Bullet point {i+1}",
                value=st.session_state["default_bullets"][i],
                disabled=st.session_state.get("disabled", False),
            )
        st.button(
            "Generate bullets using AI",
            on_click=gen_bullets,
            args=(product_name, tshirt_desc),
            disabled=st.session_state.get("disabled", False),
        )

        az = AmazonGenerator(
            brand=brand,
            client=client,
            bucket=selected_bucket,
            template_id=template_id,
            clothes_type=clothes_type,
            kids=is_for_kids,
            dont_use_caching=dont_use_caching,
        )

        if st.button("Generate TSV", key="single_gen_but"):
            # prep data for downloading
            st.session_state["running"] = True
            file_buffer = az.generate_amazon_listing(
                files_uploaded,
                product_name,
                subfolder=subfolder,
                product_title=product_title,
                product_description=product_description,
                keyphrases=st.session_state["default_keywords"],
                bullets=st.session_state["default_bullets"],
                base_price=base_price,
                additional_large_size=additional_large_size,
                new_file=True,
            )
            st.session_state.disabled = False
            file_buffer.seek(0)
            if st.download_button(
                "Download TSV",
                data=file_buffer.read().encode("utf-8"),
                file_name=f"{product_name}.tsv",
                mime="application/octet-stream",
            ):
                st.rerun()

with tab3:
    folders = gcs_list_prefixes(client, selected_bucket, "", "/")
    folder2 = st.selectbox(
        "Select your generic product folder",
        [f for f in folders],
        disabled=st.session_state.get("disabled", False),
    )
    subfolders = [
        x.split("/")[1]
        for x in gcs_list_prefixes(client, selected_bucket, folder2, "/")
    ]
    st.write("Found the following subfolders: ")
    st.markdown(f":orange[{'  ||  '.join(subfolders)}], ")

    az = AmazonGenerator(
        brand=brand,
        client=client,
        bucket=selected_bucket,
        template_id=template_id,
        clothes_type=clothes_type,
        kids=is_for_kids,
        dont_use_caching=dont_use_caching,
    )

    if st.button("Generate Table for generic design", key="generic_gen_but"):
        # prep data for downloading
        aibar = st.progress(0)
        file_buffer = az.generate_plain_product_descriptions(
            folder2,
            aibar,
        )
        st.session_state.disabled = False
        file_buffer.seek(0)
        if st.download_button(
            "Download Generic CSV",
            data=file_buffer.read().encode("utf-8"),
            file_name=f"generic-designs-{folder2}.csv",
            mime="application/octet-stream",
        ):
            st.rerun()
