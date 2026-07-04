"""
URL configuration for the landing pages plugin.

Mounted by the installer under the "p/" prefix, so pages are served at
/p/<slug>/. See the README for an optional project-level root catch-all.
"""

from django.urls import path

from . import views

app_name = "landing_pages"

urlpatterns = [
    # Order form submission
    path("api/zone/<int:zone_id>/submit-form/", views.submit_order_form, name="submit_form"),
    # Landing page display
    path("<slug:slug>/", views.landing_page_view, name="landing_page"),
]
