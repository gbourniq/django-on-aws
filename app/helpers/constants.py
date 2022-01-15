"""This module defines constants to be used across the app code base"""

from collections import namedtuple
from enum import Enum

TEMPLATE_DIR = "main"

DIMS = namedtuple("DIMS", "width height")
CROP_SIZE = DIMS(300, 300)
THUMBNAIL_SIZE = DIMS(500, 500)
IMG_EXT = ".jpg"
THUMBNAIL_SUFFIX = "_thumbnail"


class TemplateNames(Enum):
    """Enum to gather template name"""

    HOME = f"{TEMPLATE_DIR}/home.html"
    REGISTER = f"{TEMPLATE_DIR}/register.html"
    LOGIN = f"{TEMPLATE_DIR}/login.html"
    CATEGORIES = f"{TEMPLATE_DIR}/categories.html"
    ITEMS = f"{TEMPLATE_DIR}/items.html"
    CONTACT_US = f"{TEMPLATE_DIR}/contact_us.html"
    GO_BACK_HOME = f"{TEMPLATE_DIR}/go_back_home.html"
