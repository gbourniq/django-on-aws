"""This module defines all the Django views"""

import json
import logging
from typing import Union

import boto3
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View, generic

from app.config import AWS_REGION, SES_IDENTITY_ARN
from helpers import strings
from helpers.constants import TemplateNames

from .forms import ContactForm, NewUserForm
from .mixins import RequireLoginMixin
from .models import Category, Item

logger = logging.getLogger(__name__)
ses_client = boto3.client("ses", region_name=AWS_REGION)


class IndexView(generic.base.TemplateView):
    """View for home page, /"""

    template_name = TemplateNames.HOME.value

    def get(self, request, *args, **kwargs) -> render:
        return render(request, self.template_name)


class SignUpFormView(View):
    """View for users to sign up an account, /register"""

    form_class = NewUserForm
    initial = {}
    template_name = TemplateNames.REGISTER.value

    # pylint: disable=unused-argument
    def get(self, request, *args, **kwargs) -> render:
        """Logic for GET method. Renders the signup form template"""
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    # pylint: disable=unused-argument
    def post(self, request, *args, **kwargs) -> Union[render, redirect]:
        """Logic for POST method. Attempts to register and log in user"""
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            signup_message = strings.SIGNUP_MSG.format(account_name=username)
            messages.success(request, signup_message)
            logger.info(signup_message)
            login(request, user)
            if SES_IDENTITY_ARN:
                # Send email to verify the new SES identity
                try:
                    response = ses_client.verify_email_identity(
                        EmailAddress=form.cleaned_data.get("email")
                    )
                    logger.info(f"SES verify_email_identity call response: {response}")
                except Exception as ses_err:
                    logger.error(
                        f"Failed to run SES verify_email_identity: {repr(ses_err)}"
                    )
            return redirect("/")
        for msg in form.error_messages:
            messages.error(request, f"{msg}: {form.error_messages[msg]}")
        return render(request, self.template_name, {"form": form})


def logout_request(request) -> redirect:
    """Logout an authenticated user, /logout"""
    logout(request)
    messages.info(request, strings.LOGOUT)
    return redirect("/")


class LoginFormView(View):
    """Login a user, /login"""

    form_class = AuthenticationForm
    initial = {}
    template_name = TemplateNames.LOGIN.value

    # pylint: disable=unused-argument
    def get(self, request, *args, **kwargs) -> render:
        """Logic for GET method. Renders the login page"""
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    # pylint: disable=unused-argument
    def post(self, request, *args, **kwargs) -> Union[render, redirect]:
        """Logic for POST method. Attempts to log in user"""
        form = self.form_class(request=request, data=request.POST)
        if not form.is_valid():
            # User DOES NOT exist
            messages.error(request, strings.INVALID_LOGIN)
            return render(request, self.template_name, {"form": form})

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)

        login_msg = strings.LOGIN.format(username=username)
        messages.info(request, login_msg)
        logger.info(login_msg)

        if secure_page := request.GET.get("next"):
            # Redirect to the restricted page
            logger.info(strings.REDIRECT_AFTER_LOGIN.format(secure_page=secure_page))
            return redirect(secure_page)
        return redirect("/")


# pylint: disable=too-many-ancestors
class CategoriesView(generic.ListView):
    """View to display category cards"""

    template_name = TemplateNames.CATEGORIES.value
    context_object_name = "all_categories_list"
    model = Category

    def get_queryset(self):
        if categories := self.model.objects.all():
            return categories.order_by("category_name")
        raise Http404(strings.MSG_404)


class RedirectToItemView(generic.base.RedirectView):
    """
    View to redirect the user to the first item of a category when the
    category card is clicked on <category_slug>/ -> <category_slug>/<first-item-slug>
    """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """Logic for GET method"""
        category = get_object_or_404(
            Category, category_slug=self.kwargs["category_slug"]
        )
        first_item = (
            Item.objects.filter(category_name=category).order_by("item_name").first()
        )
        return f"/items/{category.category_slug}/{first_item.item_slug}/"


class ItemsView(generic.ListView):
    """View for items, /<category_slug>/<item_slug>/"""

    template_name = TemplateNames.ITEMS.value
    category = None
    item = None
    ordered_items_in_category = None

    def get_queryset(self):
        """
        Validates and retrieves the category and item objects
        according to the given <category_slug> and <item_slug>
        """
        self.category = get_object_or_404(
            Category, category_slug=self.kwargs["category_slug"]
        )
        self.item = get_object_or_404(Item, item_slug=self.kwargs["item_slug"])

        self.ordered_items_in_category = Item.objects.filter(
            category_name=self.category
        ).order_by("item_name")

        return Item.objects.get(pk=self.item.id)

    def get_context_data(self, **kwargs):
        """
        Call the base implementation first to get a context
        and loads additional values to be rendered
        """
        context = super().get_context_data(**kwargs)
        context["item"] = self.item
        context["category"] = self.category
        context["sidebar"] = self.ordered_items_in_category
        context["this_item_idx"] = list(self.ordered_items_in_category).index(self.item)
        return context

    def dispatch(self, *args, **kwargs):
        """
        Overrides the dispatch method, to increment the views field
        before returning the HTTP response.
        """
        self.get_queryset().increment_views()
        return super().dispatch(*args, **kwargs)


class ContactUsFormView(RequireLoginMixin, View):
    """View for users to send messages via the Contact Us form"""

    form_class = ContactForm
    initial = {}
    template_name = TemplateNames.CONTACT_US.value

    # pylint: disable=unused-argument
    def get(self, request, *args, **kwargs) -> render:
        """Logic for GET method"""
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    # pylint: disable=unused-argument
    def post(self, request, *args, **kwargs) -> Union[render, redirect]:
        """HTTP POST method to send an email if the form is valid."""
        form = self.form_class(request.POST)

        if not form.is_valid():
            logger.warning(strings.INVALID_FORM)
            messages.error(request, strings.INVALID_FORM)
            return render(request, self.template_name, {"form": form})

        if not settings.SNS_TOPIC_ARN:
            logger.warning(strings.SNS_TOPIC_NOT_CONFIGURED)
            messages.warning(request, strings.SNS_TOPIC_NOT_CONFIGURED_USER_FRIENDLY)
            return render(request, self.template_name, {"form": form})

        sns_client = boto3.client("sns", region_name=AWS_REGION)
        response = sns_client.publish(
            TargetArn=settings.SNS_TOPIC_ARN,
            Message=json.dumps({"default": form.cleaned_data}),
        )
        sns_response = strings.SNS_SERVICE_RESPONSE.format(response=response)
        logger.info(sns_response)

        return render(
            request,
            TemplateNames.GO_BACK_HOME.value,
            {"message": strings.CONTACTUS_FORM},
        )
