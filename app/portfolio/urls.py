"""portfolio URL Configuration"""

import debug_toolbar
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.urls import include, path, re_path
from django.views.decorators.cache import cache_page

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
CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)
CAT_PREFIX = "api/v1/categories"
ITEMS_PREFIX = "api/v1/items"

# For admin page automated translation from set locale region
urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    # If no prefix is given, use the default language
    prefix_default_language=False,
)

urlpatterns += [
    # Django rest framework
    # path(f"{CAT_PREFIX}/", CategoryList.as_view()),
    # path(f"{CAT_PREFIX}/new", CategoryCreate.as_view()),
    # path(f"{CAT_PREFIX}/<int:id>/", CategoryRetrieveUpdateDestroyAPIView.as_view(),),
    # path(f"{CAT_PREFIX}/<int:id>/stats/", CategoryStats.as_view(),),
    # path(f"{ITEMS_PREFIX}/", ItemList.as_view()),
    # path(f"{ITEMS_PREFIX}/new", ItemCreate.as_view()),
    # path(f"{ITEMS_PREFIX}/<int:id>/", ItemRetrieveUpdateDestroyAPIView.as_view()),
    # User management
    path("__debug__/", include(debug_toolbar.urls)),
    path("register/", SignUpFormView.as_view(), name="register"),
    path("login/", LoginFormView.as_view(), name="login"),
    path("logout/", logout_request, name="logout"),
    # Views
    path("", IndexView.as_view(), name="home"),
    path(
        "contact/",
        (cache_page(CACHE_TTL))(ContactUsFormView.as_view()),
        name="contact_us",
    ),
    path(
        "items/",
        (cache_page(CACHE_TTL))(CategoriesView.as_view()),
        name="categories_view",
    ),
    path(
        "items/<category_slug>/<item_slug>/",
        (cache_page(CACHE_TTL))(ItemsView.as_view()),
        name="item_view",
    ),
    path(
        "items/<category_slug>/",
        (cache_page(CACHE_TTL))(RedirectToItemView.as_view()),
        name="items_view",
    ),
    # Extra apps
    path("tinymce/", include("tinymce.urls")),
    # No url matched
    re_path(r"^.*/$", url_error, name="error404"),
]

urlpatterns = (
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + urlpatterns
)

# Custom views for errors
handler404 = "main.errors.handler404"

# Customise admin page titles
admin.site.index_title = ""
admin.site.site_header = "Tari Kitchen Admin"
