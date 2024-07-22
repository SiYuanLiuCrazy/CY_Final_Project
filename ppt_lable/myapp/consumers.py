import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ppt_id = self.scope['url_route']['kwargs']['ppt_id']
        self.group_name = f'progress_{self.ppt_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'progress_update',
                'message': data['message']
            }
        )

    async def progress_update(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
