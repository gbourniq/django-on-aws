"""This module defines general helpers to process Django objects"""

from typing import List, Union

# pylint: disable=imported-auth-user
from django.contrib.auth.models import User


def get_registered_emails() -> Union[List[str], None]:
    """Retrives email addresses of registered users."""
    if registered_email_addresses := [
        user.email for user in User.objects.all() if user.email
    ]:
        return registered_email_addresses
    return None
