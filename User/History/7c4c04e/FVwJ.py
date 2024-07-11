from .imports import *


class SignIn(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def __send_sms(user: User):
        r = user.set_verify_code()

        k = Kavenegar()
        k.lookup(user.cellphone, str(r))

        color_print(f'code "{r}" sent', 'bold')
        return

    @staticmethod
    def __bad_request(msg: str) -> Response:
        context = {
            'msg': msg
        }
        return Response(context, status=HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=ApiUserLoginView, responses={200: TokenViewDto(many=False)})
    def post(self, request):
        context = {}
        status = HTTP_200_OK

        cellphone: str = request.data.get('cellphone', request.data.get('username'))
        if len(cellphone) > 11:
            cellphone = User.remove_prev_v2(cellphone)
        if cellphone is None:
            return self.__bad_request('لطفا شماره همراه را وارد کنید')

        user: User = User.objects.filter(cellphone=cellphone, deleted=None).first()
        if user is None:
            return self.__bad_request('کاربر یافت نشد')

        if request.GET.get("is_agency"):
            err, msg = User.check_login_parameter(request.GET.get("is_agency"))
            if err is True:
                return self.__bad_request(msg)
            if user.type != 2:
                return self.__bad_request('شما دسترسی لازم را ندارید')

        if request.GET.get("is_admin"):
            err, msg = User.check_login_parameter(request.GET.get("is_admin"))
            if err is True:
                return self.__bad_request(msg)
            if user.is_superuser is False:
                return self.__bad_request('شما دسترسی لازم را ندارید')

        t = threading.Thread(
            target=self.__send_sms,
            kwargs={'user': user},
            daemon=True
        )
        # t.start()

        context['msg'] = 'کد با موفقیت ارسال شد'
        return Response(context, status=status)
