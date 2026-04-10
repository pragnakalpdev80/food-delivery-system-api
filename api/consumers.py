from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from datetime import datetime
from django.contrib.auth.models import AnonymousUser
from .models import Order,CustomerProfile,DriverProfile,Restaurant


class OrderConsumer(AsyncWebsocketConsumer):
    """ Orders notification consumer """
    @database_sync_to_async
    def user_has_access(self, user, order_number):
        """ Checks the user is the customer, restaurant owner, or assigned driver for order number. """
        try:
            order = Order.objects.select_related('customer__user', 'restaurant__owner', 'driver__user').filter(order_number=order_number).first()
            if user.user_type == 'customer':
                return order.customer.user == user
            elif user.user_type == 'restaurant_owner':
                return order.restaurant.owner == user
            elif user.user_type == 'delivery_driver':
                return order.driver is not None and order.driver.user == user
        except Exception as e:
            print(e)
            return False
        return False
    
    async def connect(self):
        """ connects to the order dashboard """
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

        
        has_access = await self.user_has_access(user, self.order_id)
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name,self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to order {self.order_id}.',
            'timestamp': datetime.now().isoformat()
        }))
        
    async def disconnect(self, close_code):
        """ disconnects from the order dashboard """
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
    """ Restaurants notification consumer """
    @database_sync_to_async
    def user_owns_restaurant(self, user, restaurant_id):
        """ Check the restaurant belongs to the connecting user. """
        try:
            return Restaurant.objects.filter(id=restaurant_id, owner=user, is_deleted=False).exists()
        except Exception:
            return False

    async def connect(self):
        """ connects to the restaurant dashboard """
        if isinstance(self.scope['user'], AnonymousUser):
            print("1")
            await self.close()
            return
        
        if not self.scope['user'].user_type == 'restaurant_owner':
            await self.close()
            print("2")
            return
             
        self.restaurant_id = self.scope["url_route"]["kwargs"]["restaurant_id"]
        self.room_group_name = f"restaurant_{self.restaurant_id}"
        user = self.scope['user']
 
        has_access = await self.user_owns_restaurant(user=user, restaurant_id=self.restaurant_id)
        if not has_access:
            print("1")
            await self.close()
            return
    
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Restaurant {self.restaurant_id} dashboard connected.',
            'timestamp': datetime.now().isoformat()
        }))

    async def disconnect(self, close_code):
        """ disconnects from the restaurant dashboard """
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except AttributeError:
            None

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

class CustomerDashboardConsumer(AsyncWebsocketConsumer):
    """ Customers notification consumer """
    async def connect(self):
        """ connects to the customer dashboard """
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
            return
        
        if not self.scope['user'].user_type == 'customer':
            await self.close()
            return

        if not self.scope['user'].customer_profile.id == self.scope["url_route"]["kwargs"]["customer_id"]:
            await self.close()
            return

        self.customer_id = self.scope["url_route"]["kwargs"]["customer_id"]
        self.room_group_name = f"customer_{self.customer_id}"
        user = self.scope["user"]

        has_access = await self.user_validation(user=user, customer_id=self.customer_id)
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Customer {self.customer_id} dashboard connected.',
            'timestamp': datetime.now().isoformat()
        }))

    async def disconnect(self, close_code):
        """ disconnects from the customer dashboard """
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
    
    @database_sync_to_async
    def user_validation(self, user, customer_id):
        """ Check the restaurant belongs to the connecting user. """
        try:
            return CustomerProfile.objects.filter(id=customer_id, user=user, is_deleted=False).exists()
        except Exception:
            return False


class DriverDashboardConsumer(AsyncWebsocketConsumer):
    """ Drivers notification consumer """
    async def connect(self):
        """ connects to the driver dashboard """
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
            return
        
        if not self.scope['user'].user_type == 'delivery_driver':
            await self.close()
            return
        
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]
        self.room_group_name = f"driver_{self.driver_id}"

        user = self.scope["user"]

        has_access = await self.user_validation(user=user, driver_id=self.driver_id)
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Driver {self.driver_id} dashboard connected.',
            'timestamp': datetime.now().isoformat()
        }))

    async def disconnect(self, close_code):
        """ disconnects from the customer dashboard """
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
    
    @database_sync_to_async
    def user_validation(self, user, driver_id):
        """ Check the restaurant belongs to the connecting user. """
        try:
            return DriverProfile.objects.filter(id=driver_id, user=user, is_deleted=False).exists()
        except Exception:
            return False

