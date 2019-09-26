import time
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import login, SESSION_KEY
from django.core.exceptions import ObjectDoesNotExist
from .models import Position, Transcript, Record, User, Join
import random
import math
from app.utils.http import JsonResponse
from app.utils.decorators import login_required
from app.utils.redisServer import record_add, get_begin_to_end_score, get_order_by_user
from django.utils import timezone
from datetime import datetime
from .config import APPID, APPSECRET
import json
import requests
from redis import Redis


rds = Redis(host='127.0.0.1', port=6379)

# Create your views here.


'''小程序接口'''


def loginUser(request):
    if request.method == "GET":
        try:
            code = request.GET.get('code')
            info = {
                'appid': str(APPID),
                'secret': str(APPSECRET),
                'js_code': str(code),
                'grant_type': 'authorization_code'
            }
            url = "https://api.weixin.qq.com/sns/jscode2session"
            r = requests.get(url, parmas=info)
            openid = r.json().get('openid')
            if openid:
                try:
                    user = User.objects.get(openid=openid)
                    user.last_login = timezone.now()
                    user.save()
                    request.session['user_id'] = User.objects.get(openid=openid).id
                    request.session.set_expiry(600)
                    login(request, user)
                    response = JsonResponse(status=True, message="老用户登录成功")
                    response.add_value('username', user.name)
                    response.add_value('std_id', user.std_id)
                    response.add_value('sex', user.sex)
                    response.add_value('wx_nickname', user.wx_nickname)
                    response.add_value('wx_avatar', user.wx_avatar)
                    response.add_value('phone', user.phone)
                    response.add_value('class', user.class_s)
                    response.add_value('major', user.major)
                    response.add_value('academy', user.academy)
                    response.add_value('is_bind', user.is_bind)
                    return response
                except ObjectDoesNotExist:
                    user = {
                        'openid': openid,
                        'is_bind': False,
                        'wx_nickname': request.GET.get('wx_nickname'),
                        'wx_avatar': request.GET.get('wx_avatar'),
                        'createTime': timezone.now(),
                        'last_login': timezone.now(),
                    }
                    login_user = User.objects.create(**user)
                    login(request, login_user)
                    record_add(login_user.id, 0)
                    return HttpResponse(json.dumps({'status': True, 'msg': '第一次登录成功'}))
            else:
                return HttpResponse(json.dumps({'status': False, 'msg': '获取openid失败'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '获取openid超时'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


def getUserInfo(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        response = JsonResponse(status=False, message="未登录")
        return response

    try:
        user = User.objects.get(id=user_id)
        response = JsonResponse(status=True, message="获取成功")
        response.add_value('username', user.name)
        response.add_value('std_id', user.std_id)
        response.add_value('sex', user.sex)
        response.add_value('wx_nickname', user.wx_nickname)
        response.add_value('wx_avatar', user.wx_avatar)
        response.add_value('phone', user.phone)
        response.add_value('class', user.class_s)
        response.add_value('major', user.major)
        response.add_value('academy', user.academy)
        return response

    except ObjectDoesNotExist:
        return JsonResponse(status=False, message="该用户不存在")


@login_required
def register(request):
    if request.method == 'POST':
        try:
            try:
                user_id = request.session[SESSION_KEY]
            except KeyError:
                response = JsonResponse(status=False, message="未登录")
                return response
            user = User.objects.get(id=user_id)
            user.name = request.POST.get("name")
            user.std_id = request.POST.get("std_id")
            user.sex = request.POST.get("sex")
            user.wx_nickname = request.POST.get("wx_nickname")
            user.wx_avatar = request.POST.get("wx_avatar")
            user.phone = request.POST.get("phone")
            user.academy = request.POST.get("academy")
            user.major = request.POST.get("major")
            user.class_s = request.POST.get("class")
            user.save()
            response = JsonResponse(status=True, message="注册成功")
            return response
        except ObjectDoesNotExist:
            response = JsonResponse(status=False, message="该用户不存在")
            return response
    else:
        response = JsonResponse(status=False, message="访问方式错误")
        return response


def getTranscriptList(request):
    if request.method == 'GET':
        transcripts = Transcript.objects.all()
        transcript_list = []

        for transcript in transcripts:
            transcript_json = {
                "id": transcript.id,
                "name": transcript.name,
                "begin_time": transformTime(transcript.start_time),
                "end_time": transformTime(transcript.end_time),
                "introduction": transcript.introduction
            }
            transcript_list.append(transcript_json)

        response = JsonResponse(status=True, message="获取全部副本成功")
        response.add_value("data", {"transcriptList": transcript_list})
        return response
    else:
        response = JsonResponse(status=False, message="访问方式错误")
        return response


@login_required
def getPositionList(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        response = JsonResponse(status=False, message="未登录")
        return response

    if request.method == 'GET':
        transcript_id = request.GET.get("id")
        positions = Position.objects.filter(transcript=transcript_id)
        position_list = []

        for position in positions:
            try:
                record = Record.objects.filter(is_signed=1).get(user=user_id, position=position.id)
                is_signed = True
                score_gain = record.score
            except ObjectDoesNotExist:
                is_signed = False
                score_gain = 0
            position_information = {
                    "id": position.id,
                    "name": position.name,
                    "introduction": position.introduction,
                    "longitude": position.longitude,
                    "latitude": position.latitude,
                    "radius": position.radius,
                    "is_signed": is_signed,
                    "image": position.image,
                    "score": position.score,
                    "score_gain": score_gain
                }
            position_list.append(position_information)

        response = JsonResponse(status=True, message='获取成功')
        response.add_value('positionList', position_list)
        return response
    else:
        response = JsonResponse(status=False, message='访问方式错误')
        return response


def getScoreOrder(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        response = JsonResponse(status=False, message='用户未登录')
        return response
    if request.method == "POST":
        rank = get_order_by_user(user_id)
        begin = request.POST.get('begin') * 10
        end = request.POST.get('end') * 10

        score = 0
        sign_list = Record.objects.filter(user_id=user.id).filter(is_signed=1)
        for sign in sign_list:
            score = score + sign.score
        
        response = JsonResponse(status=False, message='获取成功')
        user = User.objects.get(id=user_id)
        order = {
            'nickname': user.wx_nickname,
            'avatar': user.wx_avatar,
            'score': score,
            'rank': rank
        }
        orderList = []
        orders = get_begin_to_end_score(begin, end)
        for single_order in orders:
            

        response.add_value('order', order)
        response.add_value('orderList', orderList)
    else:
        response = JsonResponse(status=False, message='访问方式错误')
        return response


@login_required
def addRecord(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        response = JsonResponse(status=False, message='用户未登录')
        return response
    if request.method == 'POST':
        try:
            position_id = request.POST.get('id')
            longitude = float(request.POST.get('longitude'))
            latitude = float(request.POST.get('latitude'))
            send_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request.POST.get('time')))
            position = Position.objects.get(id=position_id)
            user = User.objects.get(id=user_id)
            try:
                Record.objects.get(user=user, position=position)
                response = JsonResponse(status=False, message='已打卡')
                return response
            except ObjectDoesNotExist:
                url = 'https://restapi.amap.com/v3/distance'
                params = {
                    'key': '0573fb2a6b6b28a0e970988cefd18e44',
                    'origins': str(longitude) + str(latitude),
                    'destination': str(position.longitude) + str(position.latitude)
                }
                r = requests.get(url, params=params)
                distance = r.json().get('results').get('distance')
                sign_time = timezone.now()
                if transformTime(position.transcript.start_time) <= transformTime(sign_time) <= transformTime(position.transcript.end_time):
                    if distance <= position.radius:
                        new_record = Record()
                        fixed_score = Position.objects.get(id=position_id).score
                        lucky_score = random.randint(fixed_score/10)
                        new_record.is_signed = True
                        new_record.score = fixed_score + lucky_score
                        new_record.time = send_time
                        new_record.created_time = sign_time
                        new_record.user = user
                        new_record.position = position
                        new_record.transcript = position.transcript
                        new_record.save()

                        record_add(user.id, fixed_score + lucky_score)

                        try:
                            Join.objects.get(user=user).filter(transcript=position.transcript)
                        except ObjectDoesNotExist:
                            join_record = {
                                'time': timezone.now(),
                                'user': user,
                                'transcript': position.transcript
                            }
                            Join.objects.create(**join_record)

                        response = JsonResponse(status=True, message='签到成功')
                        response.add_value('score', fixed_score)
                        response.add_value('lucky', lucky_score)
                        return response
                    else:
                        response = JsonResponse(status=False, message='不在打卡范围')
                        return response
                else:
                    response = JsonResponse(status=False, message='不在打卡时间范围内')
                    return response
        except KeyError:
            response = JsonResponse(status=False, message='参数错误')
            return response
    else:
        response = JsonResponse(status=False, message='访问方式错误')
        return response


'''后台接口'''


def backendIndex(request):
    user_num = User.objects.all().count()
    sign_num = Record.objects.filter(is_signed=1).count()
    activity_num = Transcript.objects.all().count()
    position_num = Position.objects.all().count()
    response = JsonResponse(status=True, message="获取成功")
    response.add_value("user_num", user_num)
    response.add_value("sign_num", sign_num)
    response.add_value("activity_num", activity_num)
    response.add_value("message_num", 0)
    response.add_value("position_num", position_num)
    response.add_value("expiry_num", 0)
    return response


def backendUser(request):
    user_list = []
    users = User.objects.all()
    for user in users:
        score = 0
        sign_number = Record.objects.filter(user_id=user.id).filter(is_signed=1).count()
        sign_list = Record.objects.filter(user_id=user.id).filter(is_signed=1)
        for sign in sign_list:
            score = score + sign.score
        result = {
            'username': user.name,
            'studentId': user.std_id,
            'sex': user.sex,
            'nickname': user.wx_nickname,
            'studentTel': user.phone,
            'college': user.academy,
            'major': user.major,
            'signNumber': sign_number,
            'score': score,
            'loginTime': user.last_login,
            'createTime': user.createTime
        }
        user_list.append(result)

    response = JsonResponse(status=True, message="获取成功")
    response.add_value("user_list", user_list)
    return response


def backendGetActivity(request):
    activity_list = []
    activities = Transcript.objects.all()
    for activity in activities:
        positions = Position.objects.filter(transcript_id=activity.id)
        position_list = []
        for position in positions:
            position_list.append(position.name)
        result = {
            'name': activity.name,
            'begin': activity.start_time,
            'end': activity.end_time,
            'introduce': activity.introduction,
            'number': activity.number,
            'place': position_list,
            'placeNum': len(position_list)
        }
        activity_list.append(result)

    response = JsonResponse(status=True, message="获取成功")
    response.add_value("activity_list", activity_list)
    return response


def backendGetFreePosition(request):
    position_list = []
    positions = Position.objects.filter(is_used=0)
    for position in positions:
        position_list.append({
            'id': position.id,
            'name': position.name
        })

    response = JsonResponse(status=True, message="获取成功")
    response.add_value("position_list", position_list)
    return response


def backendGetAllPosition(request):
    position_list = []
    positions = Position.objects.all()
    for position in positions:
        sign_number = Record.objects.filter(position=position.id).count()
        result = {
            'name': position.name,
            'longitude': position.longitude,
            'latitude': position.latitude,
            'score': position.score,
            'radius': position.radius,
            'introduce': position.introduction,
            'number': sign_number
        }
        if position.transcript:
            result['transcript'] = position.transcript.name
        else:
            result['transcript'] = '暂无'
        position_list.append(result)

    response = JsonResponse(status=True, message="获取成功")
    response.add_value("position_list", position_list)
    return response


def backendGetSign(request):
    sign_list = []
    try:
        signs = Record.objects.filter(is_signed=1).all()
        for sign in signs:
            user = User.objects.get(id=sign.user_id)
            position = Position.objects.get(id=sign.position_id)
            result = {
                'nickname': user.wx_nickname,
                'username': user.name,
                'place': position.name,
                'score': sign.score,
                'time': sign.time
            }
            sign_list.append(result)

        response = JsonResponse(status=True, message="获取成功")
        response.add_value("sign_list", sign_list)
        return response
    except ObjectDoesNotExist:
        response = JsonResponse(status=True, message="获取成功， 没有签到记录")
        response.add_value("sign_list", sign_list)
        return response


def backendAddActivity(request):
    req = json.loads(str(request.body, encoding="utf-8"))
    try:
        transcript = Transcript.objects.get(name=req.get('name'))
        return JsonResponse(status=False, message="已有该副本")
    except ObjectDoesNotExist:
        new_activity = {
            'name': req.get('name'),
            'introduction': req.get('introduction'),
            'start_time': req.get('beginTime'),
            'end_time': req.get('endTime'),
            'number': 0
        }
        Transcript.objects.create(**new_activity)
        place_list = req.get('placeList')
        for place in place_list:
            goal_place = Position.objects.get(name=place)
            goal_place.is_used = 1
            goal_place.transcript_id = Transcript.objects.get(name=new_activity['name'])
            goal_place.save()

        response = JsonResponse(status=True, message="提交成功")
        return response


def backendAddPosition(request):
    req = json.loads(str(request.body, encoding="utf-8"))
    try:
        position = Position.objects.get(name=req.get('name'))
        return JsonResponse(status=False, message="已有该地点")
    except ObjectDoesNotExist:
        new_position = {
            'name': req.get('name'),
            'longitude': req.get('longitude'),
            'latitude': req.get('latitude'),
            'introduction': req.get('introduction'),
            'score': req.get('score'),
            'radius': req.get('radius'),
            'is_used': 0,
            'transcript_id': None,
            'image': req.get('image')
        }
        Position.objects.create(**new_position)

        response = JsonResponse(status=True, message="提交成功")
        return response

#
# def backendDeletePosition(request):
#     req = json.loads(str(request.body, encoding="utf-8"))
#     try:
#         position_req = Position.objects.get(name=req.get('name'))
#         sign_list = Record.objects.filter(id=position_req.id)
#         for sign in sign_list:
#             sign.is_signed = 0
#             sign.save()
#         Position.objects.get(name=req.get('name')).delete()
#         response = JsonResponse(status=True, message="删除成功")
#         return response
#     except ObjectDoesNotExist:
#         response = JsonResponse(status=False, message="没有该地点")
#         return response


def transformTime(timeStr):
    time_cut = timeStr.split('.')
    time_str = time_cut[0]
    result = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
    return result
