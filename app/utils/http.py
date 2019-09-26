# -*- coding: utf-8 -*
__author__ = 'geebos'
import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder


class JsonResponse(HttpResponse):
    """
    json响应类
    """
    def __init__(self, data: dict=None, *, status: bool, message: str='', **kwargs):
        """
        构造函数
        :param data: 返回的数据 可为空
        :param status: 响应的状态 bool 关键字参数
        :param message: 响应的信息 str 关键字参数 可为空 一般是对错误的说明，前端用来提示
        :param kwargs: 其他参数 可忽略
        """
        kwargs.setdefault('content_type', 'application/json')
        super(JsonResponse, self).__init__(**kwargs)

        if not isinstance(status, bool):
            raise ValueError('status必须为 bool类型')
        if not isinstance(message, str):
            raise ValueError('message必须为 str类型')
        if data is None:
            self._data = {'data': {}}
        elif isinstance(data, dict):
            self._data = {'data': data}
        else:
            raise ValueError('data参数必须是 dict类型')

        self._container = []
        self._data['status'] = status
        self._data['message'] = message

    @property
    def content(self):
        self._container.insert(0, self.make_bytes(json.dumps(self._data, cls=DjangoJSONEncoder)))
        return b''.join(self._container)

    @content.setter
    def content(self, value):
        pass

    def write(self, content):
        self._container.append(self.make_bytes(content))

    def set_status(self, status: bool):
        if not isinstance(status, bool):
            raise ValueError('status必须为 bool类型')
        self._data['status'] = status

    def set_message(self, message: str):
        if not isinstance(message, str):
            raise ValueError('message必须为 str类型')
        self._data['message'] = message

    def update(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError('data参数必须是 dict类型')
        self._data['data'].update(data)

    def add_value(self, key, value):
        self._data['data'][key] = value