import logging

from django.http import Http404
from django.shortcuts import redirect, render

from helpers import strings

logger = logging.getLogger(__name__)


def error_404(request) -> redirect:
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


def handler500(request):
    """Function to handle any 500 error with a custom page"""
    logger.error(f"Internal Server Error: {request}")
    return render(
        request,
        "main/go_back_home.html",
        context={"message": strings.MSG_500, "code_handled": 500,},
    )
