# Etsy Bestseller T-Shirt Finder

A small standalone Streamlit tool (`etsy_bestsellers.py`) that finds the
high-demand men's & women's t-shirts on Etsy and lets you browse them all in
one grid.

> **Note:** This is a self-contained research tool. It is unrelated to the
> Shopify file-uploader in the rest of this repo and could live in its own
> repository if you prefer.

## Why it ranks by "favourites", not "baskets"

The "In 20 baskets" / "Bestseller" text you see on Etsy only exists on the
public listing pages, which Etsy **blocks automated tools from reading** (every
request gets an HTTP 403). That data is *not* available through Etsy's official
API to any app.

What the API *does* give us is **`num_favorers`** — how many people have
favourited a listing. This is a legitimate, public popularity signal, and
high-favourite listings are overwhelmingly the same ones that carry the
Bestseller badge. So the tool uses a **minimum-favourites threshold** as the
stand-in for your "20+ baskets" filter.

If you specifically need real basket/sales numbers, a dedicated research tool
(Alura, EtsyHunt, eRank, Sale Samurai) is the legitimate way to get them.

## Setup

1. **Get a free Etsy API keystring**
   Go to <https://www.etsy.com/developers/your-apps>, create an app, and copy
   the **keystring**. (Etsy approves these manually; it can take a little time.)

2. **Provide the key** — either:
   ```bash
   export ETSY_API_KEY="your_keystring_here"
   ```
   or just paste it into the sidebar when the app opens.

3. **Run it** (dependencies are already in `requirements.txt`):
   ```bash
   pip install -r requirements.txt
   streamlit run etsy_bestsellers.py
   ```

## Using it

- Pick **Men's / Women's / Both** and a search term (default `t-shirt`).
- Set the **minimum favourites** threshold — raise it to see only the strongest
  sellers.
- **Listings to scan** controls thoroughness: each 100 listings is one API call,
  so 500 is a good balance of speed vs. coverage.
- Press **Search Etsy**. Results come back as a grid sorted by favourites
  (most-favourited first), each linking straight to the Etsy listing. A 🔥
  marks the standout listings (2× your threshold or more).

## Limits to be aware of

- Etsy's API allows ~10,000 calls/day; this tool stays well under that.
- Etsy caps how deep you can page into search results, so "scan 1000" is a
  generous, safe ceiling — it samples the top of the results, not literally
  every t-shirt on Etsy.
