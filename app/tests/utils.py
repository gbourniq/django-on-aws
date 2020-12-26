"""This module defines helper functions for unit tests"""
import shutil
from pathlib import Path
from typing import Tuple

from django.db.models.fields.files import ImageFieldFile
from PIL import Image

from app.config import MEDIA_URL

APP_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = APP_DIR / MEDIA_URL


def create_dummy_png_image(
    image_name: str, image_size: Tuple[int, int] = (300, 300)
) -> None:
    """Creates a test PNG images"""
    Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)
    Image.new("RGB", image_size, (255, 255, 255)).save(
        f"{IMAGE_DIR}/{image_name}", "png"
    )


def create_dummy_file(filename: str) -> None:
    """Creates a test non-image files"""
    Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)
    with (Path(IMAGE_DIR) / filename).open("w", encoding="utf-8") as f:
        f.write("dummy content")


def check_image_attributes(
    image: ImageFieldFile, size_check: Tuple[int, int], ext_check: str
):
    """Asserts the given image has the expected size and extension."""
    assert Image.open(image).size == size_check
    assert Path(image.name).suffix == ext_check


def cleanup_media_dir():
    """Clean up"""
    shutil.rmtree(IMAGE_DIR)
