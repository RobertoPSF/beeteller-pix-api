from django.urls import path
from .views import generate_messages

urlpatterns = [
    path("msgs/<str:ispb>/<int:number>", generate_messages, name="generate_messages"),
]