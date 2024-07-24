import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ppt_id = self.scope['url_route']['kwargs']['ppt_id']
        self.group_name = f'progress_{self.ppt_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        self.send_task = asyncio.create_task(self.send_progress_updates())

    async def disconnect(self, close_code):
        logger.debug(f'Disconnecting from WebSocket group: {self.group_name}')

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        if hasattr(self, 'send_task'):
            self.send_task.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        logger.debug(f'Received message: {data}')

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'progress_update',
                'message': data['message']
            }
        )

    async def progress_update(self, event):
        message = event['message']
        logger.debug(f'Sending message: {message}')

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def send_progress_updates(self):
        while True:
            progress = cache.get(f"split_progress_{self.ppt_id}", {'current_page': 0, 'total_pages': 0, 'ppt_name': '无任务'})
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'progress_update',
                    'message': progress
                }
            )
            await asyncio.sleep(5)