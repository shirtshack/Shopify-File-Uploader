import os
import re
import base64
import httpx
from functools import wraps

import anthropic
from loguru import logger

from .gdrive import RestrictedWords


client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


DESCRIPTION_EXAMPLES = {
    "I'm Not Always Grumpy, Sometimes I Ride My Bicycle": """<p>Express Your Dual Personality</p>
<p>The "I'm not always GRUMPY, sometimes I ride my BICYCLE" printed T-shirt is a good blend of humor and fashion. A unique spin on casual wear that allows you to showcase your love for cycling and your spirited nature in one chic garment. Its comfortable fit and impactful design make it apt for all casual events.</p>
<p>Quality Craftsmanship</p>
<p>Enjoy both comfort and durability. Our T-shirts are crafted from pure cotton which ensures long-lasting quality and breathability. The digital printing method used produces a high-quality finish, resulting in a design that's lively and resistant to fade. Let your wardrobe make a statement about your love for cycling and your witty personality.</p>
<p>Versatile and Attractive</p>
<p>Explore your stylish flair without compromising comfort. A meticulously designed graphic tee, great for cycling enthusiasts and those who value humor in their daily life. These shirts can be paired with any bottoms making them a versatile addition to your closet. Proudly display your cycling ardor and feisty charm in a stylishly humorous way.</p>
<p>-Printed T-shirt</p>
<p>-Durable cotton fabric</p>
<p>-Fun bicycle-themed design</p>
<p>-Comfortable fit</p>
<p>-Great for casual wear</p>
""",
    "Funny Halloween": """<p>Crafted for Comfort: Halloween and Humor Combined</p>
<p>Embrace the spooky season with a sprinkle of light-hearted humor in our Halloween Funny T-Shirt. This soft style men's t-shirt is crafted from premium fabric ensuring a smooth, comfortable fit all day long. Unleash your Halloween spirit while expressing your comedic side in this unique, well-made shirt, a perfect blend of comfort, durability, and laughs.</p>
<p>Elevate Your Festive Wardrobe</p>
<p>Celebrate Halloween with style and humor. Our Halloween Funny T-Shirt is not just another piece of clothing. It's a striking balance of high-quality materials and vivid graphics. With its soft fabric and precision fit, this T- shirt is sure to make a welcome addition to your festive wardrobe, serving both comfort and chuckles.</p>
<p>Never Compromise on Quality or Fun</p>
<p>We see every t-shirt as more than just a garment. It is your statement, your comfort. With this in mind, we crafted our Halloween Funny T-Shirt from a soft, breathable fabric that is perfect for both indoor gatherings and outdoor trick-or-treating. This product is set to infuse your Halloween celebrations with an element of fun while maintaining the highest standards of quality and comfort.</p>
<p>-Soft-style cotton-blend fabric</p>
<p>-Spooky Halloween design</p>
<p>-Comfortable fit</p>
<p>-Fun twist on a classic t-shirt</p>
<p>-Perfect for costume parties</p>""",
    "I'M RETIRED NOT EXPIRED": """<p>Step into Retirement in Style and Humor</p>
<p>Celebrate the joy of a well-earned retirement with Shirtshack's IM RETIRED NOT EXPIRED t-shirt. A good blend of fun, fashion, comfort and a generous dollop of tongue-in-cheek wit. Flaunt your free status with pride with this high-quality retirement tee that defines your new phase of life in a light-hearted way. There's nothing quite like a good laugh to celebrate years of relentless hard work.</p>
<p>Quality Meets Comfort</p>
<p>Shirtshack believes that your retirement should be all about comfort. This soft, durable, and high-quality cotton t-shirt makes a bold statement without compromising on comfort. Its superior fit is designed to suit all body types and its prerequisite is to deliver maximum ease. Impeccable stitching and premium materials ensure you'll be lounging in style and luxury for years to come. </p>
<p>Gift a Gag That Lasts</p>
<p>Looking for that great retirement gift? Look no further! The IM RETIRED NOT EXPIRED shirt is not just another gift; it's a gesture, a sentiment, and a smile rolled into one. It's a good way to kick-start the golden years of a retiree's life, signaling the end of alarms and the beginning of a life ruled by their own time. Let them celebrate their freedom every time they wear it.</p>
<p>-Makes a great retirement gift</p>
<p>-Sentimental and meaningful</p>
<p>-Reminds retiree of their accomplishments</p>
<p>-Unique keepsake for the special day</p>
<p>-Highlights retiree's new beginning</p>""",
}

BULLET_EXAMPLES = {
    "I'm Not Always Grumpy, Sometimes I Ride My Bicycle": """Bullet 1: Stylish And Comfortable - The "I'm not always GRUMPY sometimes I ride my BICYCLE" printed t-shirt is a must-have for any bike enthusiast who appreciates comfort and style, crafted from premium materials for maximum durability

Bullet 2: Unique Casual Wear - Stand out from the crowd with this unique shirt that is created for cyclists. Its comfortable fit and witty print makes it an excellent choice for casual outings or bike rides

Bullet 3: Lightweight And Durable - Designed with an emphasis on wearability, this t-shirt is made of soft, high-quality fabric that not only ensures comfort but also longevity for regular use

Bullet 4 :Remarkable Design - A good gift for bike lovers, this "I'm not always grumpy" shirt boasts a clever design that is sure to put a smile on anyone's face while subtly showcasing their love for cycling

Bullet 5: Versatile and Fashionable - Whether you're out on a ride or lounging around at home, this t-shirt adds whimsical charm to your wardrobe with a reminder of your favorite pastime in a trendy way
""",
    "Funny Halloween": """Bullet 1: Premium Comfort and Unique Design - This Halloween funny T-shirt is crafted to ensure a relaxed fit. The shirt's soft style elevates the comfort factor making it a preferred choice for men seeking style and comfort

Bullet 2: Expressive Style Statement - Go beyond basics with our soft style men's T-shirt. The hilarious Halloween graphics add a quirky edge making it more than just a simple piece of apparel, a conversation starter

Bullet 3: Quality That Lasts - Experience an exceptional blend of durability and comfort. This Halloween funny T-shirt undergoes rigorous quality checks to make sure it stands the test of time while maintaining its soft style

Bullet 4: Perfect for Halloween Party - This amusing shirt is the perfect wear for a Halloween party. Put the 'Treat' in 'Trick or Treat' with this soft style men's T-shirt and show off your fun-loving spirit in style

Bullet 5: Ideal Gift Option - Whether you're planning a Halloween party or looking for a unique gift, our soft style men's T-shirt never fails to impress. Gift humor and comfort wrapped into one with this Halloween funny T-shirt""",
    "I'M RETIRED NOT EXPIRED": """Bullet 1: Celebrate The Golden Years: The IM RETIRED NOT EXPIRED gift is a good way to show your loved ones how much their dedication and hard work have meant to you over the years

Bullet 2: Ideal Retirement Present: This gift serves as a statement of appreciation for years of service, reminding our beloved retirees that retirement isn't a sign of expiration

Bullet 3: Thoughtful Design: The IM RETIRED NOT EXPIRED product features a witty and positive affirmation giving every retiree a subtle reminder of their worth and continuing importance

Bullet 4: Inspiring Message: It's designed to inspire and push retirees to stay active and resilient, promoting the concept that retirement is just the beginning of a new, exciting journey!

Bullet 5: High-Quality Product: Crafted to last, this IM RETIRED NOT EXPIRED gift is not just a keepsake, but a daily reminder of their freedom, making it an ideal token for retirement celebrations""",
}

rwords = RestrictedWords().get_trademark_words()


def block_trademarked(func):
    subcalls = 0

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal subcalls
        subcalls += 1
        output = func(*args, **kwargs)
        found_words = [word for word in rwords if word.lower() in str(output).lower()]
        if len(found_words) > 0:
            if subcalls > 2:
                logger.info(
                    f"Reached retries limit. Returning output as is. Contains TRADEMARK: {found_words} subcall level {subcalls}"
                )
                if type(output) is list:
                    filtered_output = [
                        re.sub("|".join(found_words), "", x, flags=re.IGNORECASE)
                        for x in output
                    ]
                elif type(output) is str:
                    filtered_output = re.sub(
                        "|".join(found_words), "", output, flags=re.IGNORECASE
                    )
                else:
                    raise NotImplementedError(
                        f"Trademark filtering not implemented for type: {type(output)} "
                    )
                subcalls = 0
                return filtered_output

            logger.info(
                f"Found trademark, retrying with {found_words} blocked, subcall level: {subcalls}"
            )
            kwargs["trademark_stopwords"] = [x.title() for x in found_words]
            return wrapper(*args, **kwargs)
        else:
            subcalls = 0
            return output

    return wrapper


def _call_claude(system: str, user: str, max_tokens: int = 1024) -> str:
    """Helper to call Claude and return the text response."""
    response = client.messages.create(
        model="claude-sonnet-4-5-20251001",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


def _call_claude_vision(image_url: str, prompt: str) -> str:
    """Helper to call Claude with an image URL and return the text response."""
    image_data = base64.standard_b64encode(httpx.get(image_url).content).decode("utf-8")
    # Detect media type from URL
    if image_url.lower().endswith(".png"):
        media_type = "image/png"
    elif image_url.lower().endswith(".webp"):
        media_type = "image/webp"
    elif image_url.lower().endswith(".gif"):
        media_type = "image/gif"
    else:
        media_type = "image/jpeg"

    response = client.messages.create(
        model="claude-sonnet-4-5-20251001",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )
    return response.content[0].text


class AiProductGenerator:
    """Class to generate copy for Amazon products."""

    def __init__(self, product_name, description, clothing_type) -> None:
        self.product_name = product_name
        self.image_description = description
        self.clothing_type = clothing_type

    @block_trademarked
    def generate_title(self, trademark_stopwords=None):
        """Generate a title for the product."""
        stop_phrase = ""
        if trademark_stopwords:
            stop_phrase = (
                " Refrain from using the following trademarked words or similar terms: "
                + ", ".join(trademark_stopwords)
                + ". "
            )

        system = (
            "You are a system that generates a ~20 word product title for Amazon products. "
            "Generate a product title for the given product description. "
            "Add funny and appropriate bits to make the title more interesting. "
            "Reply with only the title, no preamble."
            + stop_phrase
        )

        few_shot = f"""Product Description: A funny {self.clothing_type} called "AMONG US TRUST NO ONE" it shows many colorful aliens
Product Title: Among us trust no one, funny {self.clothing_type}, 100% Cotton, Funny {self.clothing_type}, Unisex Printed Design Ideal birthday gift for true players. Who is the impostor?
Product Description: A funny {self.clothing_type} called "BEER THERAPY" it shows a man holding a beer
Product Title: Beer Therapy {self.clothing_type} for Men - Funny and Refreshing! 100% cotton, Funny {self.clothing_type}, Unisex Printed Design. The perfect therapy session after a long day.
Product Description: A funny {self.clothing_type} called "{self.product_name}" it shows {self.image_description}
Product Title:"""

        title = _call_claude(system, few_shot, max_tokens=60)
        title = title.strip()
        logger.info(f"Created AI title: {title}")

        if len(title) > 180:
            logger.info("Title too long, retrying...")
            return self.generate_title()
        return title

    @block_trademarked
    def generate_description(self, trademark_stopwords=None):
        """Generate a description for the product."""
        stop_phrase = ""
        if trademark_stopwords:
            stop_phrase = (
                "Refrain from using the following trademarked words or similar terms: "
                + ", ".join(trademark_stopwords)
                + ". "
            )

        few_shot = (
            "Generate a description for the product, pay attention to the product type, "
            "you're only given examples for t-shirts but product type may be hoodie or sweatshirt, "
            "here are some example descriptions for t-shirts:\n\n"
            + "\n".join(
                [
                    f"Product Name: {k}\nDescription:{v}"
                    for k, v in DESCRIPTION_EXAMPLES.items()
                ]
            )
            + f"\n\n{stop_phrase}\n\nProduct Name: "
            + f"{self.product_name}\nProduct Image depicted:{self.image_description}\nClothing type: {self.clothing_type}"
            + "\nDescription:"
        )

        system = (
            "You are a system that generates a few paragraphs describing a product for an Amazon posting. "
            "Generate a product description based on the product name. "
            "Create something similar to the examples. "
            "Do not use any copyrighted brands like Disney, Marvel or Ghibli. "
            "Don't say the product is official or licensed."
        )

        desc = _call_claude(system, few_shot, max_tokens=512)
        desc = desc.replace("\n\n", "\n")
        logger.info(f"Created AI desc: {desc}")
        return desc

    @block_trademarked
    def generate_keyphrases(self, trademark_stopwords=None):
        """Generate keyphrases for the product."""
        stop_phrase = ""
        if trademark_stopwords:
            stop_phrase = (
                " Refrain from using the following trademarked words or similar terms: "
                + ", ".join(trademark_stopwords)
                + ". "
            )

        system = (
            "You are a keyphrase generation system that produces EXACTLY 5 keyphrases for Amazon products. "
            "Keywords should be relevant to the product and popular. "
            "The list of keyphrases should be comma separated. "
            "Reply with only the comma-separated keyphrases, no preamble."
            + stop_phrase
        )

        if self.image_description:
            desc_text = f" that shows {self.image_description}"
        else:
            desc_text = ""

        zero_shot = (
            f'Please generate a list of 5 keyphrases for the following product: '
            f'A funny {self.clothing_type} model named "{self.product_name}"{desc_text}.'
        )

        keyphrases_text = _call_claude(system, zero_shot, max_tokens=80)
        keyphrases = [k.strip() for k in keyphrases_text.split(",")]
        if len(keyphrases) != 5:
            logger.info("Keyphrase generation failed, retrying...")
            return self.generate_keyphrases()
        logger.info(f"Created AI keyphrases: {keyphrases}")
        return keyphrases

    @staticmethod
    def inspect_tshirt(flat_shirt_url):
        """Use Claude vision to describe what's on the t-shirt."""
        desc = _call_claude_vision(
            flat_shirt_url,
            "What is depicted on this clothing item? Describe the design/graphic on it concisely in one sentence."
        )
        logger.info("T-shirt description: " + desc)
        return desc

    @block_trademarked
    def generate_bullets(self, trademark_stopwords=None):
        """Generate bullet points for the product."""
        stop_phrase = ""
        if trademark_stopwords:
            stop_phrase = (
                "Refrain from using the following trademarked words or similar terms: "
                + ", ".join(trademark_stopwords)
                + ". "
            )

        few_shot = (
            f"Generate 5 bullet points for this funny {self.clothing_type}, "
            "do not say the product is licensed or official, here are some examples for t-shirts:\n\n"
            + "\n".join(
                [
                    f"Product Name: {k}\nBullet points:\n{v}"
                    for k, v in BULLET_EXAMPLES.items()
                ]
            )
            + f"\n\n{stop_phrase}\n\nProduct Name: "
            + f"{self.product_name} - {self.image_description}"
            + "\nYour created bullet points:"
        )

        system = (
            "You are a bullet point generation system that produces EXACTLY 5 bullet points for Amazon products. "
            "Bullet points should be relevant to the product and attractive to a reader. "
            "Create something similar to the examples given."
        )

        raw_bullets = _call_claude(system, few_shot, max_tokens=512)
        bullets = [
            re.sub(r"Bullet \d:\s", "", bullet)
            for bullet in re.split("\n+", raw_bullets)
        ]
        bullets = [b for b in bullets if b.strip()]
        if len(bullets) != 5:
            logger.info(f"Bullet generation failed, generated {len(bullets)} instead of 5, retrying...")
            return self.generate_bullets()
        logger.info(f"Created AI bullets: {bullets}")
        return bullets


DESIGN_DESCRIPTION_EXAMPLES = {
    (
        "paws",
        "a cat underwater as the character from movie Jaws",
    ): "This funny design is purrfect for cat lovers and movie geeks alike. Are you both? Great! This makes an ideal birthday gift for film connoisseurs. Funny and original design depicting a cat under water in the style of the iconic movie.",
    (
        "What part of don't you understand",
        "The phrase 'what part of don't you understand' and complicated formulas",
    ): "This funny design is an ideal gift for math and science lovers. Do you get the math in the joke? Neither do we. That is what makes this design great (statistically speaking). Don't let numbers scare you away. Wear this design and be a proud nerd. Ideal gift for your girlfriend or boyfriend.",
}

DESIGN_BULLET_EXAMPLES = {
    (
        "Skeleton Riding Mummy Dinosaur",
        "A Skeleton Riding Mummy Dinosaur",
    ): "Bullet 1: Funny Skeleton Riding Mummy Dinosaur T rex Halloween Design. Cool graphic design for trick or treating with Skull, Rib Cage, and Jack O Lantern Candy Basket or Jackolantern Pumpkin. Perfect trick or treat design for prehistoric animal lovers. \nBullet 2: Scary Halloween design for men, women, boys, girls who love dinosaurs. Creepy design for All Hallows Eve, Day of the Dead, All Souls Day, Halloween Party or Ghoulish Theme Party.",
    (
        "Three Possum Moon",
        "three opossums singing at the moon",
    ): "Bullet 1: In the cursed Three Opossum Moon region, possums don't just howl, they channel magical energy from the moon. Ever heard of the 3 Possum Moon meme? It's more than a joke - it's a nod to the mystical magic of the Possum race. \nBullet 2: The Three Possum Moon isn't just a fashion statement. Rumor has it, it's magic. Those who wear it speak of mysterious possum encounters as it's said to tap into the Possom Kingdome's mystical power. Wear if you dare!",
}


class AiDesignGenerator:
    """Class to generate copy for Amazon Merch designs."""

    def __init__(self, product_name, description) -> None:
        self.product_name = product_name
        self.image_description = description

    @staticmethod
    def inspect_design(design_url):
        """Use Claude vision to describe the design."""
        desc = _call_claude_vision(
            design_url,
            "Describe this design/graphic concisely in one sentence."
        )
        logger.info("Design description: " + desc)
        return desc

    @block_trademarked
    def generate_title(self, trademark_stopwords: list = None):
        """Generate a title for the design."""
        stop_phrase = ""
        if trademark_stopwords:
            stop_phrase = (
                "VERY IMPORTANT! Refrain from using the following trademarked words or similar terms: "
                + ", ".join(trademark_stopwords)
                + ". "
            )

        few_shot = f"""Design Description: A funny design called "AMONG US TRUST NO ONE" it shows many colorful aliens
        Design Title: Among us trust no one design - Ideal birthday gift for true players. Who is the impostor?
        Design Description: A funny design called "BEER THERAPY" it shows a man holding a beer
        Design Title: Beer Therapy design - The perfect therapy session after a long day.
        Design Description: A funny design called "ALL MIGHT SMASH" it shows hero academia
        Design Title: All Might Smash design - Show the world your heroic spirit! Plus Ultra!
        ------ END OF EXAMPLES ----\n{stop_phrase}\n
        Design Description: A funny design called "{self.product_name}" it shows {self.image_description}
        Design Title:"""

        system = (
            f"You are a system that generates an ~8 word product title for Amazon merch items. "
            f"Generate a title for the given design description. "
            f"Add funny and appropriate bits to make the title more interesting. "
            f"Reply with only the title, no preamble.{stop_phrase}"
        )

        title = _call_claude(system, few_shot, max_tokens=60)
        title = title.strip()
        logger.info(f"Created AI title: {title}")

        if len(title) > 180:
            logger.info("Title too long, retrying...")
            return self.generate_title()
        return title

    @block_trademarked
    def generate_description(self, trademark_stopwords: list = None):
        """Generate a description for the design."""
        stop_phrase = ""
        if trademark_stopwords:
            stop_phrase = (
                "VERY IMPORTANT! NEVER use the following trademarked words in the description: "
                + ", ".join(trademark_stopwords)
                + ". "
            )

        few_shot = (
            "Generate a description for the design based on the following examples:\n\n"
            + "\n\n".join(
                [
                    f"Design Name: {k[0]}\nDesign shows: {k[1]}\nDescription: {v}"
                    for k, v in DESIGN_DESCRIPTION_EXAMPLES.items()
                ]
            )
            + f"\n------- END OF EXAMPLES ---------\n{stop_phrase}\n"
            + "\nDesign Name: "
            + f"{self.product_name}\nDesign shows: {self.image_description}"
            + "\nDescription:"
        )

        system = (
            "You are a system that generates a few paragraphs describing a Design for an Amazon Merch posting. "
            "Generate a Design description based on the design name and a short description. "
            "Create something similar to the examples. "
            "Do not use any copyrighted brands like Disney, Marvel or Ghibli. "
            "Don't say the product is official or licensed."
        )

        desc = _call_claude(system, few_shot, max_tokens=512)
        logger.info(f"Created AI desc: {desc}")
        return desc

    @block_trademarked
    def generate_bullets(self, trademark_stopwords: list = None):
        """Generate bullet points for the design."""
        stop_phrase = ""
        if trademark_stopwords:
            stop_phrase = (
                "VERY IMPORTANT! NEVER use the following trademarked phrases in the bulletpoints: "
                + ", ".join(trademark_stopwords)
                + ". "
            )

        few_shot = (
            "Generate 2 bullet points for this funny design, do not say the product is licensed or official, "
            "here are some examples:\n\n"
            + "\n".join(
                [
                    f"Design Name: {k[0]}\nDesign Description: {k[1]}\nBullet points:\n{v}"
                    for k, v in DESIGN_BULLET_EXAMPLES.items()
                ]
            )
            + f"\n------- END OF EXAMPLES ---------\n{stop_phrase}\n"
            + "\n\nDesign Name: "
            + f"{self.product_name}\nDesign Description: {self.image_description}"
            + "\nYour created bullet points:"
        )

        system = (
            "You are a bullet point generation system that produces EXACTLY 2 bullet points for Amazon designs. "
            "Bullet points should be relevant to the design and attractive to a reader. "
            "Create something similar to the examples given. "
            "You're not allowed to use any copyrighted brands like Disney, Marvel or Ghibli."
        )

        raw_bullets = _call_claude(system, few_shot, max_tokens=512)
        bullets = [
            re.sub(r"Bullet \d:\s", "", bullet)
            for bullet in re.split("\n+", raw_bullets)
        ]
        bullets = [b for b in bullets if b.strip()]
        if len(bullets) != 2 or any(len(b) > 255 for b in bullets):
            logger.info(f"Bullet generation failed, generated {len(bullets)}, retrying...")
            return self.generate_bullets()
        logger.info(f"Created AI bullets: {bullets}")
        return bullets
