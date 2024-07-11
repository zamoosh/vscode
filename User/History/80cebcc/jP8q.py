from rest_framework import serializers
from client.admin_v2.serializers import UserSerializer
from car.admin_v2.serializers import CarTicketSerializer
from car.api_v2.serializers import TravelSerializer
from ticket.models import Ticket, Message
from library.mongo import PyMongo
from colorful_logging import c_print
import bson


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Message
        exclude = ['deleted']


class BaseTicketSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(allow_null=True)
    active_device = serializers.SerializerMethodField(allow_null=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'created_at', 'updated_at', 'user', 'active_device', 'status', 'number']

    def get_active_device(self, obj: Ticket):
        if obj.active_device_access is None:
            return None
        if obj.active_device_access.active_device is None:
            return None

        return CarTicketSerializer(obj.active_device_access.active_device).data

    def get_user(self, obj: Ticket):
        if obj.user is None:
            return None
        return UserSerializer(obj.user).data

    def get_status(self, obj: Ticket):
        status = {
            'name': '',
            'value': obj.status
        }
        if obj.status == 0:
            status['name'] = 'خوانده نشده'
        elif obj.status == 1:
            status['name'] = 'پاسخ داده شده'
        elif obj.status == 2:
            status['name'] = 'باید بعدا چک شود'
        return status


class TicketSingleSerializer(BaseTicketSerializer):
    CAR_STATE = PyMongo('carstates')

    message_set = MessageSerializer(many=True)
    gps = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = BaseTicketSerializer.Meta.model
        fields = BaseTicketSerializer.Meta.fields + ['message_set', 'gps']

    @classmethod
    def get_gps(cls, obj: Ticket):
        try:
            car = obj.active_device_access.active_device
            cls.CAR_STATE.aggregate_query.append({
                '$match': {
                    'carID': car.device.imei if car.old_id is None else bson.ObjectId(car.old_id),
                    'coordinates': {"$ne": None}
                }
            })
            cls.CAR_STATE.aggregate_query.append({'$sort': {'postTime': -1}})
            cls.CAR_STATE.aggregate_query.append({
                '$lookup': {
                    'from': 'carstates',
                    'localField': 'carID',
                    'foreignField': 'carID',
                    'as': 'lpt'
                }
            })
            cls.CAR_STATE.aggregate_query.append({
                '$unwind': {
                    'preserveNullAndEmptyArrays': True,
                    'path': '$lpt'
                }
            })
            cls.CAR_STATE.aggregate_query.append({
                '$addFields': {
                    'last_post_time': '$lpt.postTime'
                }
            })
            cls.CAR_STATE.aggregate_query.append({'$limit': 1})
            data = list(
                cls.CAR_STATE.aggregate(cls.CAR_STATE.aggregate_query)
            )
            cls.CAR_STATE.aggregate_query.clear()

            if len(data) == 0:
                print("\n[ticket single admin]: len of data is zero\n")
                return None

            json_data = {}
            json_data.update(data[0])
            json_data['imei'] = car.device.imei
            c_print(f'End getting point data for ticket {obj.id}', "green")
            return TravelSerializer(json_data).data
        except Exception as e:
            c_print(e)
        return None


class ReadLatencySerializer(serializers.ModelSerializer):
    class Meta:
        pass
