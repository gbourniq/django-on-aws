"""This module defines helper functions for unit tests"""
from pathlib import Path
from typing import Tuple

from django.db.models.fields.files import ImageFieldFile
from PIL import Image


def create_dummy_png_image(
    dir_path: Path, image_name: str, image_size: Tuple[int, int] = (300, 300)
) -> None:
    """Creates a test PNG images"""
    Image.new("RGB", image_size, (255, 255, 255)).save(
        f"{dir_path}/{image_name}", "png"
    )


def create_dummy_file(dir_path: Path, filename: str) -> None:
    """Creates a test non-image files"""
    with (dir_path / filename).open("w", encoding="utf-8") as f:
        f.write("mock content")


def check_image_attributes(image: ImageFieldFile, size: Tuple[int, int], ext: str):
    """Asserts the given image has the expected size and extension."""
    assert Image.open(image).size == size
    assert Path(image.name).suffix == ext
