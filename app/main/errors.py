"""This module defines error handlers"""

import logging

from django.http import Http404
from django.shortcuts import redirect, render

from helpers import strings

logger = logging.getLogger(__name__)


def url_error(request) -> redirect:
    """Handles unmatched URLs"""
    raise Http404(strings.MSG_404)


def handler404(request, exception) -> render:
    """Function to handle any 404 error with a custom page"""
    logger.error(f"{str(exception)}")
    return render(
        request,
        "main/go_back_home.html",
        context={"message": f"{str(exception)}", "code_handled": 404},
    )
