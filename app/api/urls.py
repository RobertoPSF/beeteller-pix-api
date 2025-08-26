from django.urls import path

from .views import stream_start, stream_continue_or_delete


urlpatterns = [
    path("pix/<str:ispb>/stream/start", stream_start, name="stream_start"),
    path("pix/<str:ispb>/stream/<str:interation_id>",
        stream_continue_or_delete,
        name="stream_continue_or_delete",
    ),
]
