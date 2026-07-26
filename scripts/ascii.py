"""ASCII art generator from profile images."""

import os
from typing import Optional

import numpy as np
from PIL import Image

from logger import logger
from paths import PathManager
from constants import DEFAULT_ASCII_WIDTH as ASCII_WIDTH, DEFAULT_ASCII_CHARSET as ASCII_CHARSET

ASSET_ASCII_DIR = PathManager.ASSET_ASCII_DIR
ASSET_IMAGE_DIR = PathManager.ASSET_IMAGE_DIR


def image_to_ascii(
    image_path: str,
    width: int = ASCII_WIDTH,
    charset: str = ASCII_CHARSET,
) -> str:
    """Convert an image file to an ASCII art string.

    Args:
        image_path: Path to the source image.
        width: Character width of the output ASCII art.
        charset: Characters used from darkest to lightest.

    Returns:
        A multi-line string containing the ASCII representation.
    """
    try:
        img = Image.open(image_path).convert("L")
    except (FileNotFoundError, OSError) as exc:
        logger.error(f"Cannot open image at {image_path}: {exc}")
        return ""

    aspect_ratio = img.height / img.width
    height = int(width * aspect_ratio * 0.55)
    img = img.resize((width, height))

    pixels: np.ndarray = np.array(img)
    char_count = len(charset)

    lines: list[str] = []
    for row in pixels:
        line = "".join(charset[int(pixel / 256 * char_count)] for pixel in row)
        lines.append(line)

    return "\n".join(lines)


def generate_ascii(
    source: Optional[str] = None,
    output_name: str = "profile.txt",
) -> Optional[str]:
    """Generate ASCII art from the profile image and save to the ascii assets dir.

    Args:
        source: Path to the source image.  Defaults to ``assets/image/profile.jpg``.
        output_name: Filename for the saved ASCII output.

    Returns:
        The generated ASCII string, or ``None`` on failure.
    """
    if source is None:
        source = str(ASSET_IMAGE_DIR / "profile.jpg")

    if not os.path.isfile(source):
        logger.warning(f"Source image not found: {source}")
        return None

    ascii_art = image_to_ascii(source)
    if not ascii_art:
        return None

    output_path = os.path.join(str(ASSET_ASCII_DIR), output_name)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ascii_art)

    logger.info(f"ASCII art saved to {output_path}")
    return ascii_art
