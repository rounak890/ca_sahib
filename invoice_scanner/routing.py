from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/ca_sahib/$", consumers.ChatConsumer.as_asgi()),
]
