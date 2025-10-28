"""
ASGI config cho dự án webrtc.
Cấu hình này bọc ứng dụng Django tiêu chuẩn bằng Channels.
"""
import os
import django

from django.core.asgi import get_asgi_application

# Import các thành phần của Channels
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack 
from channels.security.websocket import AllowedHostsOriginValidator

import streaming.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webrtc.settings')

# Phải gọi django.setup()
django.setup()

# Lấy ứng dụng HTTP (phải sau khi setup)
django_asgi_app = get_asgi_application()

# Định nghĩa ứng dụng Channels
application = ProtocolTypeRouter({
    
    # Xử lý các yêu cầu HTTP bình thường
    "http": django_asgi_app, 
    
    # Xử lý các yêu cầu WebSocket
    "websocket": AllowedHostsOriginValidator( 
        AuthMiddlewareStack( 
            URLRouter(
                # Trỏ đến danh sách URL của WebSocket
                streaming.routing.websocket_urlpatterns
            )
        )
    ),
})