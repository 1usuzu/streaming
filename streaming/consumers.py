import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        """Được gọi khi một client (JS) cố gắng kết nối."""
        
        # 1. Lấy room_id từ URL (vd: /ws/chat/room1/)
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # 2. Lấy thông tin người dùng (từ AuthMiddlewareStack)
        self.user = self.scope["user"]

        # 3. Kiểm tra xem người dùng đã đăng nhập chưa
        if not self.user.is_authenticated:
            await self.close() # Từ chối kết nối nếu chưa đăng nhập
            return

        # 4. Tham gia nhóm (room)
        # Tất cả mọi người trong cùng một nhóm sẽ nhận được tin nhắn
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 5. Chấp nhận kết nối
        await self.accept()
        print(f"WS: User '{self.user.username}' connected to chat room '{self.room_id}'")

    async def disconnect(self, close_code):
        """Được gọi khi kết nối bị đóng."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"WS: User '{self.user.username}' disconnected from chat room '{self.room_id}'")

    async def receive(self, text_data):
        """Được gọi khi máy chủ nhận được tin nhắn từ client (JS)."""
        
        text_data_json = json.loads(text_data)
        message = text_data_json['message'].strip()
        
        if not message:
            return # Bỏ qua tin nhắn trống

        username = self.user.username
        
        # Lấy vai trò (Streamer/Viewer) của người dùng
        # Phải dùng sync_to_async vì .groups.filter là hoạt động DB (đồng bộ)
        @sync_to_async
        def get_user_role(user):
            if user.groups.filter(name='Streamers').exists():
                return 'streamer'
            return 'viewer'
        
        role = await get_user_role(self.user)

        # Gửi tin nhắn đến tất cả mọi người trong nhóm (room)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', # Sẽ gọi hàm 'chat_message' bên dưới
                'message': message,
                'username': username,
                'role': role
            }
        )

    async def chat_message(self, event):
        """Hàm này được gọi khi nhận được event 'chat_message' từ group_send."""
        
        # Gửi tin nhắn xuống cho client (JavaScript)
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'role': event['role']
        }))