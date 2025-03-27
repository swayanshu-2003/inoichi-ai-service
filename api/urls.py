from django.urls import path
from .views import ExtractSymptomsView

urlpatterns = [
    path("analyze-symptoms/", ExtractSymptomsView.as_view(), name="extract-symptoms"),
]
