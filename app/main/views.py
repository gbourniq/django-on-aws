import logging
from typing import Union

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import BadHeaderError, send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View, generic

from .forms import ContactForm, NewUserForm
from .mixins import RequireLoginMixin
from .models import Category, Item
from .tasks import send_email_celery

logger = logging.getLogger(__name__)


class IndexView(generic.base.TemplateView):
    """
    View for home page, /
    """

    template_name = "main/home.html"

    def get(self, request, *args, **kwargs) -> render:
        return render(request, self.template_name)


class SignUpFormView(View):
    """
    View for users to sign up an account, /register
    """

    form_class = NewUserForm
    initial = {}
    template_name = "main/register.html"

    def get(self, request, *args, **kwargs) -> render:
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs) -> Union[render, redirect]:
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"New account created: {username}")
            logger.info(f"User {username} successfully registered.")
            login(request, user)
            return redirect("/")
        [
            messages.error(request, f"{msg}: {form.error_messages[msg]}")
            for msg in form.error_messages
        ]
        return render(request, self.template_name, {"form": form})


def logout_request(request) -> redirect:
    """
    Logout an authenticated user, /logout
    """
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("/")


class LoginFormView(View):
    """
    Login a user, /login
    """

    form_class = AuthenticationForm
    initial = {}
    template_name = "main/login.html"

    def get(self, request, *args, **kwargs) -> render:
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs) -> Union[render, redirect]:
        form = self.form_class(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                logger.info(f"User {username} successfully logged in.")
                if request.GET.get("next"):
                    return redirect(request.GET.get("next"))
                else:
                    return redirect("/")
        messages.error(request, "Invalid username or password.")
        return render(request, self.template_name, {"form": form})


class CategoriesView(generic.ListView):
    """
    View to display category cards
    """

    template_name = "main/categories.html"
    context_object_name = "all_categories_list"
    model = Category

    def get_queryset(self):
        categories = Category.objects.all()
        if categories:
            return categories.order_by("category_name")
        raise Http404("Oops.. No category found!")


class RedirectToItemView(generic.base.RedirectView):
    """
    View to redirect the user to the first item of 
    a category when the category card is clicked on.
    <category_slug>/ -> <category_slug>/<first-item-slug>
    """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        category = get_object_or_404(
            Category, category_slug=self.kwargs["category_slug"]
        )
        items_in_category = Item.objects.filter(category_name=category)
        if items_in_category:
            first_item = items_in_category.order_by("item_name").first()
            return f"/items/{category.category_slug}/{first_item.item_slug}/"
        raise Http404(f"Oops.. Category {category} does not contain any item!")


class ItemsView(generic.ListView):
    """
    View for items, /<category_slug>/<item_slug>/
    """

    template_name = "main/items.html"
    category = None
    item = None
    ordered_items_in_category = None

    def get_queryset(self):
        """
        Validates and retrieve the category and item objects
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
        context["this_item_idx"] = list(self.ordered_items_in_category).index(
            self.item
        )
        return context

    def dispatch(self, *args, **kwargs):
        self.get_queryset().increment_views()
        return super().dispatch(*args, **kwargs)


class ContactUsFormView(RequireLoginMixin, View):
    """
    View for users to send messages via
    the Contact Us form
    """

    form_class = ContactForm
    initial = {}
    template_name = "main/contact_us.html"

    def get(self, request, *args, **kwargs) -> render:
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    def email_data(self) -> dict:
        """
        Generates email data: subject, message, from_email, to_emails
        """
        body = (
            f"Name: {self.form.cleaned_data['name']}\n\n"
            f"Contact email: {self.form.cleaned_data['contact_email']}\n\n"
            f"Message: \n{self.form.cleaned_data['message']}"
        )
        return {
            "subject": self.form.cleaned_data["subject"],
            "message": body,
            "from_email": settings.EMAIL_HOST_USER,
            "recipient_list": [settings.EMAIL_HOST_USER],
        }

    def post(self, request, *args, **kwargs) -> Union[render, redirect]:
        """
        Overrides the HTTP POST method to send an email if the form
        is valid. The email task may be Asynchronous if a BROKER_URL is set.
        """
        form = self.form_class(request.POST)

        if form.is_valid():

            if not settings.EMAIL_HOST_USER:
                logger.warning(
                    f"User posted ContactForm but EMAIL_HOST_USER not set."
                )
                raise Http404("Oops.. Looks like this is not implemented yet.")

            self.form = form

            try:
                if hasattr(settings, "BROKER_URL"):
                    send_email_celery.delay(**self.email_data())
                else:
                    send_mail(**self.email_data())
            except BadHeaderError:
                raise Http404("Email function returned BadHeaderError.")
            logger.info(f"Message sent successfully: {self.email_data()}")
            messages.success(request, "Message sent successfully.")
            return render(
                request,
                "main/go_back_home.html",
                {"message": "Success! Thank you for your message."},
            )

        logger.warning("Email form is invalid.")
        return render(request, self.template_name, {"form": form})


def error_404(request) -> redirect:
    """
    Handles unmatched URLs
    """
    raise Http404("Oops.. There's nothing here.")


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
        context={
            "message": "Internal Server Error (500)",
            "code_handled": 500,
        },
    )
