### APP CONSTANTS

# BUCKET_NAME = {
#     "The Shirt Shack": "shirtshack-images",
#     "Nexgen Clothing": "nexgen-designs",
#     "PrintBar": "printbar-designs",
#     "Cobbs Prints": "david-cobb",
#     "Bananaboat": "bannanaboat ",
#     "Britains Finest": "britains-finest",
# }
DEFAULT_KEYWORDS = [
    "Fun printed t shirt",
    "Clever pun t-shirt",
    "Soft, comfortable fabric",
    "exclusive design",
    "Funny unisex t-shirt",
]
DEFAULT_BULLETS = [
    "Great Gifts For Him: Surprise your loved ones with this Funny T Shirt that's sure to bring laughter wherever it's worn. Ideal as a lighthearted grandad gift for him or her or mens birthday present. ",
    "Personalised T Shirt UK Fashion: This tee isn't just funny, it's custom-made with bold prints that humorously stand out. Represent your personality with our personalised novelty t-shirts and be the life of the party",
    "For All the Funny Men Out There: Tired of traditional men's clothing? Our Funny T Shirt is the new cool! It makes a brilliant gift, especially for those wanting to show off their quirky side",
    "Unique Presents for Men: Looking for something different from the usual mens tshirts UK has to offer? Why not consider our Funny T Shirt? It's a gift that'll uniquely make them smile every time they wear it",
    "Quality Custom T Shirt: Crafted from quality, soft, and durable material, this unisex printed t-shirt is not just funny, it is also comfortable to wear. Great for daily wear or special occasion",
]

DEFAULT_PRICE = {
    (True, "t-shirt"): 9.99,
    (True, "hoodie"): 17.99,
    (True, "sweatshirt"): 14.99,
    (False, "t-shirt"): 22.0,
    (False, "hoodie"): 19.99,
    (False, "sweatshirt"): 16.99,
}


### TSV GENERATION CONSTANTS

SIZE_VARIANTS = ["S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL"]
KIDS_SIZES = [(5, 6), (7, 8), (9, 11), (12, 13)]
# COLOR_VARIANTS = [
#     "Black",
#     "White",
#     "Charcoal",
#     "Navy",
#     "Olive",
#     "Burgundy",
#     "Grey",
#     "forest",
#     "Brown",
#     "Yellow",
#     "Green",
#     "Red",
# ]
COLOR_ALIASES = {"Burgundy": ["Burg"], "Grey": ["Gray", "sp-grey"]}

# COLOR_MAP = {
#     "Black": "Black",
#     "White": "White",
#     "Charcoal": "Grey",
#     "Navy": "Blue",
#     "Olive": "Green",
#     "Burgundy": "Red",
#     "Grey": "Grey",
#     "forest": "Green",
#     "Brown": "Brown",
#     "Yellow": "Yellow",
#     "Red": "Red",
#     "Green": "Green",
# }

CLOTHES_SUFFIX = {"t-shirt": "-T", "hoodie": "-HDY", "sweatshirt": "-SWT"}

PARENT_FIELDS = [
    "feed_product_type",
    "item_sku",
    "brand_name",
    "item_name",
    "manufacturer",
    "recommended_browse_nodes",
    "main_image_url",
    "parent_child",
    "variation_theme",
    "update_delete",
    "product_description",
    "bullet_point1",
    "bullet_point2",
    "bullet_point3",
    "bullet_point4",
    "bullet_point5",
]

SIZE_MAP = {
    "S": "Small",
    "M": "Medium",
    "L": "Large",
    "XL": "X-Large",
    "XXL": "XX-Large",
    "3XL": "XXX-Large",
    "4XL": "XXXX-Large",
    "5XL": "XXXXX-Large",
}

NON_GENERIC_BRANDS = ["The Shirt Shack"]
PRODUCT_NAME_PHRASE = {
    "t-shirt": "T-Shirt",
    "hoodie": "Hoodie UK Funny, Funny Hoodie, Unisex Printed Design HDY Ideal Hoody Funny Print, Great Birthday Idea!",
    "sweatshirt": "Sweatshirt UK Funny, Funny Sweatshirt, Unisex Printed Design swt-shrt Ideal Sweatshirt Funny Print, Great Birthday Idea!",
}
GOOGLE_STORAGE_URL = "https://storage.googleapis.com"

MAX_NAME_SKU_LENGTH = 40

CSV_CACHE_BUCKET = "amazon-uploader-cache"
