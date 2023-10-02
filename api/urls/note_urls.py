from django.urls import path
from api.views import note_views as views

urlpatterns = [
    path("", views.getNotes, name="notes"),
]