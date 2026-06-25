"""
Etsy Bestseller T-Shirt Finder
------------------------------
A small Streamlit tool that searches Etsy's *official* API (Open API v3) for
men's / women's t-shirts and ranks them by how many people have favourited
them.

Why favourites and not "baskets"?
    Etsy does NOT expose cart/basket counts or the "Bestseller" badge through
    its API -- that text only exists on the public listing pages, which Etsy
    blocks bots from reading. The number of favourites ("num_favorers") IS
    available through the API and is the closest legitimate, public signal of
    demand. High-favourite listings are overwhelmingly the same ones carrying
    the Bestseller badge.

Run it:
    1. Get a free Etsy API keystring: https://www.etsy.com/developers/your-apps
    2. export ETSY_API_KEY="your_keystring"   (or paste it in the sidebar)
    3. streamlit run etsy_bestsellers.py
"""

import os
import time

import httpx
import streamlit as st

ETSY_BASE = "https://openapi.etsy.com/v3/application/listings/active"
PER_PAGE = 100  # Etsy hard max per request
SORT_ON = "score"  # relevancy/popularity ordering we then re-rank by favourites


# --------------------------------------------------------------------------- #
# Etsy API
# --------------------------------------------------------------------------- #
def fetch_listings(api_key, keywords, pages_to_scan, min_price, max_price):
    """Page through Etsy active listings and return raw listing dicts.

    Each page is one API call (Etsy allows ~10k/day), so we cap the scan depth.
    """
    headers = {"x-api-key": api_key}
    collected = []
    progress = st.progress(0.0, text="Searching Etsy…")

    with httpx.Client(timeout=30) as client:
        for page in range(pages_to_scan):
            params = {
                "keywords": keywords,
                "limit": PER_PAGE,
                "offset": page * PER_PAGE,
                "sort_on": SORT_ON,
                "sort_order": "down",
                "includes": "Images,Shop",
            }
            if min_price:
                params["min_price"] = min_price
            if max_price:
                params["max_price"] = max_price

            resp = client.get(ETSY_BASE, headers=headers, params=params)
            if resp.status_code == 401:
                st.error("Etsy rejected the API key (401). Check the keystring.")
                break
            if resp.status_code == 429:
                st.warning("Hit Etsy's rate limit (429) — stopping early with what we have.")
                break
            if resp.status_code != 200:
                st.error(f"Etsy returned HTTP {resp.status_code}: {resp.text[:200]}")
                break

            results = resp.json().get("results", [])
            if not results:
                break
            collected.extend(results)
            progress.progress((page + 1) / pages_to_scan,
                              text=f"Scanned {len(collected)} listings…")
            time.sleep(0.2)  # stay well under the rate limit

    progress.empty()
    return collected


def normalise(listing):
    """Pull the handful of fields we display out of a raw Etsy listing."""
    price = listing.get("price") or {}
    amount = price.get("amount")
    divisor = price.get("divisor") or 100
    price_str = f"{amount / divisor:.2f}" if amount is not None else "?"

    images = listing.get("images") or []
    img = images[0].get("url_570xN") if images else None

    shop = listing.get("shop") or {}

    return {
        "title": listing.get("title", "(untitled)"),
        "favourites": listing.get("num_favorers", 0) or 0,
        "price": price_str,
        "currency": price.get("currency_code", ""),
        "url": listing.get("url"),
        "image": img,
        "shop": shop.get("shop_name", ""),
    }


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="Etsy Bestseller T-Shirt Finder", layout="wide")
st.title("👕 Etsy Bestseller T-Shirt Finder")
st.caption(
    "Searches Etsy's official API for men's & women's t-shirts and ranks them "
    "by **favourites** — the legitimate public stand-in for basket/bestseller "
    "data (which Etsy does not expose to any app)."
)

with st.sidebar:
    st.header("Search")
    api_key = st.text_input(
        "Etsy API keystring",
        value=os.getenv("ETSY_API_KEY", ""),
        type="password",
        help="Free from https://www.etsy.com/developers/your-apps",
    )
    gender = st.radio("Category", ["Men's", "Women's", "Both"], horizontal=True)
    base_kw = st.text_input("Search term", value="t-shirt")
    min_favs = st.number_input(
        "Minimum favourites (demand threshold)",
        min_value=0, value=500, step=50,
        help="The favourites equivalent of your '20+ baskets' filter. "
             "Raise it to see only the very strongest sellers.",
    )
    pages = st.slider(
        "Listings to scan", min_value=100, max_value=1000, value=500, step=100,
        help="Each 100 listings = 1 API call. Higher = more thorough, slower.",
    ) // PER_PAGE
    col_a, col_b = st.columns(2)
    min_price = col_a.text_input("Min £", value="")
    max_price = col_b.text_input("Max £", value="")
    go = st.button("Search Etsy", type="primary", use_container_width=True)


def keywords_for(gender_choice, term):
    if gender_choice == "Men's":
        return f"mens {term}"
    if gender_choice == "Women's":
        return f"womens {term}"
    return term


if go:
    if not api_key:
        st.error("Enter your Etsy API keystring in the sidebar first.")
        st.stop()

    raw = fetch_listings(
        api_key=api_key,
        keywords=keywords_for(gender, base_kw),
        pages_to_scan=pages,
        min_price=min_price.strip() or None,
        max_price=max_price.strip() or None,
    )

    items = [normalise(x) for x in raw]
    items = [i for i in items if i["favourites"] >= min_favs]
    items.sort(key=lambda i: i["favourites"], reverse=True)

    st.subheader(f"{len(items)} t-shirts with {min_favs}+ favourites")
    if not items:
        st.info("No listings cleared the threshold. Lower it or scan more listings.")
    else:
        cols = st.columns(4)
        for idx, item in enumerate(items):
            with cols[idx % 4]:
                if item["image"]:
                    st.image(item["image"], use_container_width=True)
                hot = "🔥 " if item["favourites"] >= min_favs * 2 else ""
                st.markdown(f"**{hot}{item['favourites']:,} favourites**")
                st.markdown(f"[{item['title'][:70]}]({item['url']})")
                st.caption(f"{item['currency']} {item['price']} · {item['shop']}")
else:
    st.info("Set your filters in the sidebar and press **Search Etsy**.")
