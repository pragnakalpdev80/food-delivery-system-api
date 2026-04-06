from channels.generic.websocket import AsyncWebsocketConsumer
import json
from datetime import datetime
from django.contrib.auth.models import AnonymousUser


class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
            return
         # print(f"Connection from: {self.scope['client']}")
         # print(f"Path: {self.scope['path']}")
         # print(f"User: {self.scope['user']}")
         # print(f"User: {self.scope['user'].user_type}")
        user = self.scope['user']

        self.order_id = self.scope["url_route"]["kwargs"]["order_number"]
        self.room_group_name = f"order_{self.order_id}"

        await self.channel_layer.group_add(self.room_group_name,self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to order {self.order_id}.',
            'timestamp': datetime.now().isoformat()
        }))
        
    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except AttributeError:
            None

    async def receive(self,text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "greeting_message",
                "message" : message
            })

    async def greeting_message(self, event):
        message = event['message']
        
        await self.send(text_data=json.dumps({
            'message': message
        }))
    
    async def order_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'order_status_update',
            'status': event['status'],
            'message': event['message'],
            'timestamp': datetime.now().isoformat()
        }))

    async def new_order(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'order_id': event['order_id'],
            'message': event['message'],
            'timestamp': datetime.now().isoformat()
        }))


class RestaurantDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
            return
        
        if not self.scope['user'].user_type == 'restaurant_owner':
            await self.close()
            return

        self.restaurant_id = self.scope["url_route"]["kwargs"]["restaurant_id"]
        self.room_group_name = f"restaurant_{self.restaurant_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Restaurant {self.restaurant_id} dashboard connected.',
            'timestamp': datetime.now().isoformat()
        }))

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except AttributeError:
            None

    # async def receive(self, text_data):
    #     pass

    async def new_order(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'order_id': event['order_id'],
            'message': event['message'],
            'timestamp': datetime.now().isoformat()
        }))

    async def order_status_update(self, event):
         # print(event)
        await self.send(text_data=json.dumps({
            'type': 'order_status_update',
            'status': event['status'],
            'message': event['message'],
            'timestamp': datetime.now().isoformat()
        }))

class CustomerDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
            return
        
        if not self.scope['user'].user_type == 'customer':
            await self.close()
            return

        self.customer_id = self.scope["url_route"]["kwargs"]["customer_id"]
        self.room_group_name = f"customer_{self.customer_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Customer {self.customer_id} dashboard connected.',
            'timestamp': datetime.now().isoformat()
        }))

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except AttributeError:
            None

    async def receive(self, text_data):
        pass

    async def new_order(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'order_id': event['order_id'],
            'message': event['message'],
            'timestamp': datetime.now().isoformat()
        }))

    async def order_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'order_status_update',
            'status': event['status'],
            'message': event['message'],
            'timestamp': datetime.now().isoformat()
        }))

class DriverDashboardConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
            return
        
        if not self.scope['user'].user_type == 'delivery_driver':
            await self.close()
            return
        
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]
        self.room_group_name = f"driver_{self.driver_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Driver {self.driver_id} dashboard connected.',
            'timestamp': datetime.now().isoformat()
        }))

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except AttributeError:
            None

    async def receive(self, text_data):
        pass

    async def assigned_order(self, event):
        await self.send(text_data=json.dumps({
            'type': 'assigned_order',
            'order_id': event['order_id'],
            'message': event['message'],
            'timestamp': datetime.now().isoformat()
        }))

    async def order_status_update_driver(self, event):
        await self.send(text_data=json.dumps({
            'type': 'order_status_update',
            'status': event['status'],
            'message': event['message'],
            'timestamp': datetime.now().isoformat()
        }))

