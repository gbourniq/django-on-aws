"""portfolio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from main import api_views, views

app_name = "main"  # here for namespacing of urls.

urlpatterns = [
    # Django rest framework
    path("api/v1/categories/", api_views.CategoryList.as_view()),
    path("api/v1/categories/new", api_views.CategoryCreate.as_view()),
    path(
        "api/v1/categories/<int:id>/",
        api_views.CategoryRetrieveUpdateDestroyAPIView.as_view(),
    ),
    path(
        "api/v1/categories/<int:id>/stats/", api_views.CategoryStats.as_view(),
    ),
    path("api/v1/items/", api_views.ItemList.as_view()),
    path("api/v1/items/new", api_views.ItemCreate.as_view()),
    path(
        "api/v1/items/<int:id>/",
        api_views.ItemRetrieveUpdateDestroyAPIView.as_view(),
    ),
    # User management
    path("register/", views.SignUpFormView.as_view(), name="register"),
    path("login/", views.LoginFormView.as_view(), name="login"),
    path("logout/", views.logout_request, name="logout"),
    # Views
    path("", views.IndexView.as_view(), name="home"),
    path("contact/", views.ContactUsFormView.as_view(), name="contact_us"),
    path("items/", views.CategoriesView.as_view(), name="categories_view"),
    path(
        "items/<category_slug>/<item_slug>/",
        views.ItemsView.as_view(),
        name="item_view",
    ),
    path(
        "items/<category_slug>/",
        views.RedirectToItemView.as_view(),
        name="items_view",
    ),
    # Extra apps
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    # No url matched
    re_path(r"^.*/$", views.error_404, name="error404"),
]

urlpatterns = (
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + urlpatterns
)

# Custom views for 404 and 500
handler404 = "main.views.handler404"
handler500 = "main.views.handler500"
