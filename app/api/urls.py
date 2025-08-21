from django.urls import path

from .views import stream_start


urlpatterns = [
    path("pix/<str:ispb>/stream/start", stream_start, name="stream_start"),
]
