from django.core.exceptions import ObjectDoesNotExist
from .http import JsonResponse
def login_required(func):
    def login_verification(request):
        if request.method == 'POST':
            try:
                # user = request.user
                opendId = request.POST.get("openid")
                return func(request)
            except ObjectDoesNotExist:
                response = JsonResponse(status=False,message="openid 不存在")
                return response
        else:
            response = JsonResponse(status=False, message="访问方式错误")
            return response
    return login_verification



