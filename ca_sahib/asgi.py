import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import invoice_scanner.routing  # make sure this matches your app name

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ca_sahib.settings")
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            invoice_scanner.routing.websocket_urlpatterns
        )
    ),
})
