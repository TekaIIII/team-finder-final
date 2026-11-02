from hashlib import sha256
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from .constants import AVATAR_FONT_NAME, AVATAR_FONT_SIZE, AVATAR_PALETTE, AVATAR_SIZE


def create_avatar(name, email):
    email = email.strip().lower()
    email_hash = sha256(email.encode("utf-8")).digest()
    color_index = email_hash[0] % len(AVATAR_PALETTE)
    background_color, text_color = AVATAR_PALETTE[color_index]

    name = name.strip()
    if name:
        letter = name[0].upper()[:1]
    else:
        letter = "?"

    font_path = settings.BASE_DIR / "static" / "fonts" / AVATAR_FONT_NAME
    font = ImageFont.truetype(str(font_path), size=AVATAR_FONT_SIZE)
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color=background_color)
    drawing = ImageDraw.Draw(image)

    bounds = drawing.textbbox((0, 0), letter, font=font)
    # Учитываем отступы буквы внутри шрифта.
    letter_width = bounds[2] - bounds[0]
    letter_height = bounds[3] - bounds[1]
    left = (AVATAR_SIZE - letter_width) // 2 - bounds[0]
    top = (AVATAR_SIZE - letter_height) // 2 - bounds[1]
    drawing.text((left, top), letter, font=font, fill=text_color)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())
