"""
URL configuration for the CMS plugin.

Mounted by the installer at the project root (empty prefix). Because the
installer appends this block at the END of the project's urlpatterns, every
existing project route matches first; only unmatched paths fall through to the
landing-page catch-all here.

Order matters: the API endpoint and the blog/content routes (which carry their
own prefixes) are declared BEFORE the ``<slug>`` catch-all, which must stay the
final pattern so unknown slugs 404 as before.
"""

from django.urls import include, path

from . import views

app_name = "cms"

urlpatterns = [
    # Order form submission (explicit prefix, before the catch-all).
    path("api/zone/<int:zone_id>/submit-form/", views.submit_order_form, name="submit_form"),
    # Blog posts + content pages (prefixed internally via conf; names join the "cms" namespace).
    path("", include("apps.cms.urls_blog")),
    # Landing page display — ROOT CATCH-ALL, must remain LAST.
    path("<slug:slug>/", views.landing_page_view, name="page"),
]
