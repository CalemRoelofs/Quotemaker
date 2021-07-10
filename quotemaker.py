import csv
import logging
import os
import random
import time
import requests
import spacy
import markovify

from colour_constants import colour_constants as colour
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from typing import List


class Font:
    """Font class used to make structuring text properties
    for writing over the image easier.
    """

    font_file: str
    """The name of the file with extension in the fonts folder."""
    font_colour: colour.RGB
    """The primary colour of the text to be displayed over the image."""
    font_shadow: colour.RGB
    """The shadow/background colour of the text behind the main text."""
    font_size: int
    """The size of the text to be displayed on the image."""

    def __init__(
        self,
        font_file: str,
        font_colour: colour.RGB,
        font_shadow: colour.RGB,
        font_size: int,
    ) -> None:
        self.font_file = font_file
        self.font_colour = font_colour
        self.font_shadow = font_shadow
        self.font_size = font_size


def get_image(w: int, h: int, count: int = 0) -> bytes:
    """Retrieves a rqandom image from unsplash to use as the background.

    Args:
        w (int): Width of the image
        h (int): Height of the image
        count (int, optional): Used for recrsively calling this function if
                               the first call to unsplash fails, doesn't need
                               to be set when called.

    Returns:
        bytes: The byte data of the image.
    """
    response = requests.get(f"https://source.unsplash.com/random/{w}x{h}")
    logging.debug(response.headers)
    if response.status_code != 200:
        logging.error(
            f"Error getting image from Unisplash! Response: ({response.status_code})\nTrying again ({count})"
        )
        # retries unsplash 3 times before giving up
        if count <= 3:
            time.sleep(5)
            get_image(w, h, count + 1)
        else:
            logging.error("Made > 3 attempts to get image from unsplash, aborting!")
            quit()
    return response.content


def generate_model():
    """Generates the Markovify model and saves to to JSON."""
    nlp = spacy.load("en_core_web_sm")
    logging.info("Loaded NLP")
    with open("quotes.txt") as quotesfile:
        quotes_doc = nlp(quotesfile.read()[0:1000000])
    logging.info("Loaded quotes_doc")
    quotes_sents = " ".join(
        [sent.text for sent in quotes_doc.sents if len(sent.text) > 1]
    )
    logging.info("Loaded quotes_sents")
    with open("model.json", "w") as jsonfile:
        text_model = markovify.Text(quotes_sents, state_size=3)
        jsonfile.write(text_model.to_json())
    return None


def get_ai_quote(max_chars: int = 100) -> str:
    """Generates a random quote from the Markov model saved in

    Args:
        max_chars (int, optional): Max length of the sentence to be generated. Defaults to 100.

    Returns:
        str: The generated sentence.
    """
    try:
        with open("model.json", "r") as jsonfile:
            quote_generator = markovify.Text.from_json(jsonfile.read())
            logging.info("Created Generator")
    except FileNotFoundError:
        logging.error(
            "Could not find 'model.json' file. \
            \nPlease call generate_model() before attempting to use generate_ai_quote()!"
        )
        quit()

    return quote_generator.make_short_sentence(max_chars=100)


def get_quote() -> str:
    """Returns an actual quote from 'quotes_all.csv'

    Returns:
        [type]: [description]
    """
    try:
        with open("quotes_all.csv", "r") as quotes_csv:
            quotes = list(csv.reader(quotes_csv, delimiter=";"))[2:]
    except FileNotFoundError:
        logging.error("Cannot find 'quotes_all.csv' file!\nExiting...")
        quit()

    index = random.randint(0, len(quotes))
    return quotes[index]


def block_quote(quote: str, line_length: int) -> List[str]:
    """Helper function to split quote into an array of lines.

    Args:
        quote (str): The quote to split up.
        line_length (int): The index at which to split the quote.

    Returns:
        List[str]: Array of strings made from teh quote split every `x` characters
    """
    word_list = quote.split(" ")
    print(word_list)
    lines = []
    buffer = ""
    for index, word in enumerate(word_list):
        if (index + 1) == len(word_list):
            buffer += f"{word}"
            lines.append(buffer)
        elif (len(buffer) + len(word)) < line_length:
            buffer += f"{word} "
        else:
            lines.append(buffer)
            buffer = f"{word} "
    return lines


def draw_text(
    image_bytes: bytes,
    font_data: Font,
    image_text: List[str],
    author: str = "Michael Scott",
) -> bytes:
    """Function used to draw the text onto an image

    Args:
        image_bytes (bytes): The image file loaded up as bytes
        font_data (Font): An instance of the Font class created before calling this function.
        image_text (List[str]): The array of strings made up of the split quote returned from block_quote()
        author (str, optional): [description]. Who too accredit the quote to. Defaults to "Michael Scott".

    Returns:
        bytes: The image with the text drawn onto it in byte format.
    """
    font_colour = (
        font_data.font_colour.red,
        font_data.font_colour.green,
        font_data.font_colour.blue,
    )
    font_shadow = (
        font_data.font_shadow.red,
        font_data.font_shadow.green,
        font_data.font_shadow.blue,
    )

    # Parse the image bytes into a BytesIO object
    image_object = BytesIO(image_bytes)
    image = Image.open(image_object)
    draw = ImageDraw.Draw(image)

    # Try to load the font file
    try:
        font = ImageFont.truetype(f"fonts/{font_data.font_file}", font_data.font_size)
    except OSError:
        logging.error(
            f"Cannot find font '{font_data.font_file}'! Did you put it in the 'fonts' directory?"
        )
        quit()

    # Draw the main body of text line by line
    for index, line in enumerate(image_text):
        draw.text((50, 50 * (index + 1)), line, font_shadow, font=font)
        draw.text((48, (50 * (index + 1)) - 2), line, font_colour, font=font)

    # Draw the author name in the bottom right corner
    draw.text((600, 420), f"- {author}", font_shadow, font=font)
    draw.text((598, 418), f"- {author}", font_colour, font=font)

    buf = BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()


def create_quote_image(
    font_file: str,
    font_colour: colour.RGB,
    font_shadow: colour.RGB,
    font_size: int,
    show_author: bool = False,
) -> bytes:
    """Main entry point to create an image with a quote written on it.

    Args:
        font_file (str): See `Font` class
        font_colour (colour.RGB): See `Font` class
        font_shadow (colour.RGB): See `Font` class
        font_size (int): See `Font` class
        show_author (bool, optional): True to show an author or false to default to Michael Scott. Defaults to False.

    Returns:
        bytes: The image bytes returned from draw_text()
    """
    image_bytes = get_image(900, 500)
    quote = get_ai_quote()
    logging.debug(quote)
    split_quote = block_quote(quote, 35)
    font = Font(font_file, font_colour, font_shadow, font_size)
    if show_author:
        with open("authors.txt") as authors:
            # Only get authors where the name is less than 12 characters
            # because I haven't bothered trying to implement dynamic
            # placing of the author's name on the image yet.
            authors = [a for a in authors.read().split("\n") if len(a) < 12]
        image = draw_text(
            image_bytes,
            font,
            split_quote,
            author=authors[random.randint(0, len(authors) - 1)],
        )
    else:
        image = draw_text(image_bytes, font, split_quote)

    return image


if __name__ == "__main__":
    try:
        with open("model.json") as _:
            pass
    except FileNotFoundError:
        logging.warning(
            "Could not find model.json, generating model now... (This might take a few minutes)"
        )
        generate_model()
    finally:
        image_bytes = create_quote_image(
            "Sweet Iced Coffee.ttf", colour.WHITE, colour.BLACK, 50, True
        )
        # Saves the generated file to the output
        # folder with a timestamp as the filename.
        with open(f"output{os.path.sep}{time.time()}.jpeg", "wb") as outfile:
            outfile.write(image_bytes)
