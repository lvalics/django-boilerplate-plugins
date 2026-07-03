from django.urls import path

from .views import ip_lookup_view

app_name = "web_security"

urlpatterns = [
    path("ip-lookup/<str:ip_address>/", ip_lookup_view, name="ip_lookup"),
]
