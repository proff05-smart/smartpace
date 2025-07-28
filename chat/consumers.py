import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import PrivateMessage
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async


User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.me = self.scope["user"]
        self.other_username = self.scope["url_route"]["kwargs"]["username"]

        if not self.me.is_authenticated:
            await self.close()
            return

        self.room_name = self.get_room_name(self.me.username, self.other_username)
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    def get_room_name(self, u1, u2):
        return f"{min(u1, u2)}_{max(u1, u2)}"

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")

        if message:
            timestamp = timezone.now().isoformat()
            sender = self.me
            receiver = await self.get_user(self.other_username)

            # Save message to database
            msg_obj = await self.save_message(sender, receiver, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": sender.username,
                    "timestamp": timestamp,
                    "message_id": msg_obj.id,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
            "message_id": event["message_id"],
        }))

    @database_sync_to_async
    def save_message(self, sender, receiver, content):
        return PrivateMessage.objects.create(sender=sender, receiver=receiver, content=content)

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)
