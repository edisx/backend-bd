from django.urls import path
from api.views import actionlog_views as views


urlpatterns = [
    path("", views.getActionLogs, name="actionlogs"),
]