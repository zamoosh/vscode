from .imports import *

REDIS_CONF = {
    'host': os.getenv('REDIS_HOST'),
    'port': int(os.getenv("REDIS_PORT")),
    'db': int(os.getenv("REDIS_DB")),
    'password': os.getenv('REDIS_PASS'),
    'max_connections': 500,
}

REDIS_POOL = redis.ConnectionPool(
    **REDIS_CONF
)


# REDIS_CONN: redis.Redis = redis.Redis(
#     connection_pool=REDIS_POOL,
#     decode_responses=True
# )


class Command(APIView):
    permission_classes = [IsAuthenticated]
    COMMANDS = PyMongo("commands")
    ACTIVE_GPS_LOG = PyMongo('active_gps_log')
    RESPONSES = PyMongo("responses")
    pattern = r'\$\{param.\w*\}'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text_result: str = ""
        self.car_id: str = ""
        self.command: dict = {}
        self.imei: str = ''
        self.res: dict = {}
        self.gps_response: str = ""
        self.event: threading.Event = threading.Event()
        self.pubsub_prop = {
            'ip': None,
            'port': None
        }
        self.pubsub = None

    @staticmethod
    def publish_msg(msg: str, channel: str, name: str, ttl: int = 10):
        msg_key: str = str(uuid4())
        msg = f'{msg}|{msg_key}'
        with redis.Redis(
                connection_pool=REDIS_POOL,
                decode_responses=True,
        ) as REDIS_CONN:
            REDIS_CONN.client_setname(f'django_{name}')
            REDIS_CONN.publish(channel, msg)
            REDIS_CONN.setex(msg_key, ttl, msg)
        return

    def get_producer_chan(self):
        return f'{self.imei}_socket'

    def get_receiver_chan(self):
        return f'{self.imei}_django'

    def get(self, request, model: str):
        status = HTTP_200_OK
        commands = list(
            self.COMMANDS.filter(
                {"models": model},
                count=self.COMMANDS.db.count_documents({}),
                order='-priority'
            )
        )
        if len(commands) == 0:
            status = HTTP_400_BAD_REQUEST
            return Response(
                {'msg': 'دستوری برای این مدل یافت نشد'},
                status=status
            )
        cmd_serializer = CommandSerializer(commands, many=True)
        # if 'If-None-Match' in request.headers:
        #     status = HTTP_304_NOT_MODIFIED
        text: str = f'model: {model} | command count: {len(cmd_serializer.data)}'
        color_print(text, 'pink', True, 'CMD LOG')
        return Response(cmd_serializer.data, status=status)

    def post(self, request):
        color_print(f'\n\nstart of command api\n\n', 'pink')
        if isinstance(request.user, AnonymousUser):
            return Response(
                {'msg': 'کاربر یافت نشد، لطفا از برنامه خارج شده و مجددا لاگین کنید'},
                status=HTTP_400_BAD_REQUEST
            )

        color_print("\n\ncommand api 1\n\n", 'pink')

        user = User.objects.filter(cellphone=request.user.cellphone, deleted=None)
        if not user.exists():
            return Response(
                {'msg': 'کاربر یافت نشد، لطفا از برنامه خارج شده و مجددا لاگین کنید'},
                status=HTTP_400_BAD_REQUEST
            )

        color_print("\n\ncommand api 2\n\n", 'pink')

        if settings.LOCAL:
            return Response({'msg': "شما به سرور لوکال وصل هستید"}, status=HTTP_400_BAD_REQUEST)

        self.imei = request.data.get("IMEI")

        car: ActiveDevice = ActiveDevice.objects.prefetch_related(
            Prefetch(
                lookup='device',
                queryset=Device.objects.prefetch_related(
                    Prefetch(
                        lookup='model',
                        queryset=DeviceModel.objects.filter(deleted=None)
                    ),
                ).filter(deleted=None)
            ),
            Prefetch(
                lookup='power_sys',
                queryset=PowerSys.objects.filter(deleted=None)
            )
        ).filter(
            deleted=None,
            device__imei=self.imei,
        ).first()
        if car is None:
            return Response({
                'msg': "دستگاه یافت نشد",
                'isOnline': False
            }, status=HTTP_400_BAD_REQUEST)
        if car.device.model.internet is False:
            return Response({
                'msg': "ارسال به صورت پیامک",
                'isOnline': False
            }, status=HTTP_400_BAD_REQUEST)

        color_print("\n\ncommand api 3\n\n", 'pink')

        connected_gps = self.ACTIVE_GPS_LOG.get({'imei': self.imei})
        if connected_gps is None:
            return Response({
                'msg': "(متصل نیست) ارسال به صورت پیامک",
                'isOnline': False
            }, status=HTTP_400_BAD_REQUEST)

        color_print("\n\ncommand api 4\n\n", 'pink')

        command_id = request.data.get("commandId")
        if command_id is None:
            return Response({'msg': "آی‌دی دستور نباید خالی باشد"})
        if bson.ObjectId.is_valid(command_id) is False and not ("TCPDATA=.FSCONFIG" in command_id):
            return Response({'msg': "آی‌دی دستور معتبر نیست"})
        elif bson.ObjectId.is_valid(command_id):
            command_id = bson.ObjectId(command_id)
            self.command = self.COMMANDS.get({"_id": command_id})
        elif "TCPDATA=.FSCONFIG" in command_id:
            self.command = {
                "command": command_id,
            }
        else:
            return Response({'msg': "آی‌دی دستور معتبر نیست"})
        # self.command = self.COMMANDS.get({"_id": command_id})

        color_print("\n\ncommand api 5\n\n", 'pink')

        # === COMMAND HAS ARG === #
        if re.search(self.pattern, self.command.get("command")):
            param_list = request.data.get("parameters")
            self.command["command"] = re.sub(
                self.pattern,
                lambda match: str(param_list.pop(0)),
                self.command.get("command")
            )
            color_print(self.command.get("command"), 'bold', True, "CMD")
        # === END COMMAND HAS ARG === #

        msg = self.command.get("command")
        color_print(f'command: {msg}', 'yellow')

        try:
            color_print("\n\ncommand api 6\n\n", 'pink')
            t = threading.Thread(target=self.__receiver, kwargs={}, daemon=True)
            t.start()
            Command.publish_msg(msg=msg, channel=self.get_producer_chan(), name=self.imei)
            color_print("\n\ncommand api 7\n\n", 'pink')
        except redis.ConnectionError as e:
            print("could not connect to redis!", e)
            text = (
                f"درحال حاضر سرویس در دسترس نیست"
                f" err: {e}"
            )
            return Response({'msg': text}, status=HTTP_503_SERVICE_UNAVAILABLE)

        try:
            # t = threading.Thread(target=self.__receiver, kwargs={}, daemon=True)
            # t.start()

            t2 = threading.Thread(target=self.__check_reach_time, kwargs={}, daemon=True)
            t2.start()

            self.event.wait()
            color_print("event is set", "green")

            self.pubsub.unsubscribe(self.get_receiver_chan())

            t3 = threading.Thread(target=self.__close_redis__conns, kwargs={}, daemon=True)
            t3.start()
            # del self.pubsub
            # self_client_list: list[dict] = list(
            #     filter(
            #         lambda item: item['name'] == f'django_{self.imei}' or len(item['name'].strip()) == 0,
            #         redis.Redis(**REDIS_CONF).client_list()
            #     )
            # )
            # client_list: list[int] = list(map(lambda item: item['id'], self_client_list))
            # for client in client_list:
            #     print(client)
            #     redis.Redis(**REDIS_CONF).execute_command('CLIENT', 'KILL', 'ID', client)

        except Exception as e:
            # settings.CONSOLE_LOGGER.error(str(e))
            color_print(f'error of threading: {e}', 'red', True, 'SOCKET ERR')
            self.res = Response({"isOnline": False}, status=HTTP_200_OK)

        # === PROCESS RESPONSE === #
        self.res = self.__extract_msg()
        result = self.__save_response_mongo()
        self.res.update({"responseId": str(result.get("_id"))})
        response_data = ResponseSerializer(result).data
        self.res.update({"response": response_data})
        # === END PROCESS RESPONSE === #

        return Response(self.res, status=HTTP_200_OK)

    def __close_redis__conns(self):
        self.pubsub.unsubscribe(self.get_receiver_chan())
        self_client_list: list[dict] = list(
            filter(
                lambda item: item['name'] == f'django_{self.imei}' or len(item['name'].strip()) == 0,
                redis.Redis(**REDIS_CONF).client_list()
            )
        )
        client_list: list[int] = list(map(lambda item: item['id'], self_client_list))
        for client in client_list:
            # print(client)
            redis.Redis(**REDIS_CONF).execute_command('CLIENT', 'KILL', 'ID', client)

        color_print("redis conns closed")

        return

    def __check_reach_time(self):
        if settings.LOCAL:
            c = 10
        else:
            c = 20
        while not self.event.is_set() and c > 0:
            text: str = f'still in check reach time, {c}'
            color_print(text, "dark yellow")
            time.sleep(1)
            c -= 1
        self.event.set()
        return

    def __receiver(self):
        with redis.Redis(
                connection_pool=REDIS_POOL,
                decode_responses=True,
        ) as REDIS_CONN:
            REDIS_CONN.client_setname(f'django_{self.imei}')
            pubsub = REDIS_CONN.pubsub()
            pubsub.subscribe(self.get_receiver_chan())
            self.pubsub_prop['ip'] = pubsub.connection.__dict__.get("_sock").getsockname()[0]
            self.pubsub_prop['port'] = pubsub.connection.__dict__.get("_sock").getsockname()[1]
            self.pubsub = pubsub

            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    cmd = message['data']

                    if isinstance(cmd, bytes):
                        cmd = cmd.decode('utf-8')

                    key = cmd.split('|')[-1]
                    msg_text: str = cmd.split('|')[0]

                    self.gps_response = msg_text
                    self.res = Response({"result": self.gps_response}, status=HTTP_200_OK)
                    color_print("done with consuming", "cyan", True, 'SUCCESS')
                    self.event.set()
                    REDIS_CONN.delete(key)
                    break

        return

    def get_redis_addr(self):
        return f'{self.pubsub_prop["ip"]}:{self.pubsub_prop["port"]}'

    def __extract_msg(self) -> dict:
        context = {}
        if self.gps_response != "":
            try:
                res_list = self.gps_response
                result = ",".join(res_list.split(",")[4:-1])
                # result = res_list.split(",")[-2]
                # if self.command.get("command") == "TCPDATA=.STATUS?&":
                #     result = res_list
                # color_print(result)
                context['isOnline'] = True
                self.text_result = result
                self.status = 1
            except (AttributeError, Exception) as e:
                color_print(f"ResponseApi is not standard. error: {str(e)}", 'red', True, "ERROR")
                context['isOnline'] = False
            finally:
                context['responseId'] = str(bson.ObjectId())
        else:
            color_print(f'response is empty.', 'red', True, 'RESPONSE ERR')
            self.status = 0
            context['isOnline'] = False
        return context

    def __save_response_mongo(self) -> dict:

        def save_to_mongo():
            self.RESPONSES.create(response)
            color_print('!success!', 'green', True, 'RESPONSE')
            return

        response = {}
        response['commandTitle'] = self.command.get("title")
        response['command'] = self.command.get("command")
        response['IMEI'] = self.imei
        response['car'] = str(self.car_id)
        response['registerDate'] = self.request.user.date_joined
        response['status'] = self.status
        response['user'] = self.request.user.id
        response['execDate'] = datetime.datetime.now() if self.status == 1 else None
        response['response'] = {"text": self.text_result} if self.status == 1 else None

        if self.command.get("parentId"):
            parent_cmd = self.COMMANDS.get({"id": self.command.get("parentId")})
            response['subGroupTitle'] = parent_cmd.get("title")
        else:
            response['subGroupTitle'] = "Django Added"

        t = threading.Thread(target=save_to_mongo, kwargs={}, daemon=True)
        t.start()

        color_print("command response saved", 'bold')
        return response
