from django.urls import path

from .views import DownloadRequestAPIView


urlpatterns = [
    path(
        "downloads/request/",
        DownloadRequestAPIView.as_view(),
        name="download-request",
    ),
]