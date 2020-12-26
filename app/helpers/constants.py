from enum import Enum

TEMPLATE_DIR = "main"


class TemplateNames(Enum):
    """Enum to contain template name"""

    HOME = f"{TEMPLATE_DIR}/home.html"
    REGISTER = f"{TEMPLATE_DIR}/register.html"
    LOGIN = f"{TEMPLATE_DIR}/login.html"
    CATEGORIES = f"{TEMPLATE_DIR}/categories.html"
    ITEMS = f"{TEMPLATE_DIR}/items.html"
    CONTACT_US = f"{TEMPLATE_DIR}/contact_us.html"
    GO_BACK_HOME = f"{TEMPLATE_DIR}/go_back_home.html"
