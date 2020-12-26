"""portfolio URL Configuration"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

# from main.api_views import (
#     CategoryCreate,
#     CategoryList,
#     CategoryRetrieveUpdateDestroyAPIView,
#     CategoryStats,
#     ItemCreate,
#     ItemList,
#     ItemRetrieveUpdateDestroyAPIView,
# )
from main.errors import url_error
from main.views import (
    CategoriesView,
    ContactUsFormView,
    IndexView,
    ItemsView,
    LoginFormView,
    RedirectToItemView,
    SignUpFormView,
    logout_request,
)

app_name = "main"  # here for namespacing of urls.

CAT_PREFIX = "api/v1/categories"
ITEMS_PREFIX = "api/v1/items"

urlpatterns = [
    # Django rest framework
    # path(f"{CAT_PREFIX}/", CategoryList.as_view()),
    # path(f"{CAT_PREFIX}/new", CategoryCreate.as_view()),
    # path(f"{CAT_PREFIX}/<int:id>/", CategoryRetrieveUpdateDestroyAPIView.as_view(),),
    # path(f"{CAT_PREFIX}/<int:id>/stats/", CategoryStats.as_view(),),
    # path(f"{ITEMS_PREFIX}/", ItemList.as_view()),
    # path(f"{ITEMS_PREFIX}/new", ItemCreate.as_view()),
    # path(f"{ITEMS_PREFIX}/<int:id>/", ItemRetrieveUpdateDestroyAPIView.as_view()),
    # User management
    path("register/", SignUpFormView.as_view(), name="register"),
    path("login/", LoginFormView.as_view(), name="login"),
    path("logout/", logout_request, name="logout"),
    # Views
    path("", IndexView.as_view(), name="home"),
    path("contact/", ContactUsFormView.as_view(), name="contact_us"),
    path("items/", CategoriesView.as_view(), name="categories_view"),
    path("items/<category_slug>/<item_slug>/", ItemsView.as_view(), name="item_view",),
    path("items/<category_slug>/", RedirectToItemView.as_view(), name="items_view"),
    # Extra apps
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    # No url matched
    re_path(r"^.*/$", url_error, name="error404"),
]

urlpatterns = (
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + urlpatterns
)

# Custom views for 404 and 500
handler404 = "main.errors.handler404"
