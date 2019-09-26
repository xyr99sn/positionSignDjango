中南初印象服务端

python 3.6.4+

### 一、项目说明

1、不要提交migrations文件夹里的文件

2、依赖全部在 `requirements.txt` 里，使用命令 `pip install -r requirements.txt` 安装依赖

3、依次执行命令 `python manage.py makemigrations` 和 `python manage.py migrate`  同步数据库

4、使用自定义的 `JsonResponse` 类规范化返回数据的格式，使用方法看后面的说明

### 二、编码规范

1、每个函数和类都需要解释文档，用来说明该函数或类的用途以及函数的参数的意义，原理复杂的函数还需要说明实现的逻辑。如：

```python
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
        # 设置响应头
        kwargs.setdefault('content_type', 'application/json')
        ...
```

2、不要使用无意义的变量名，如确实必要请注释说明

3、tab缩进为四个空格

4、添加必要的注释

### 三、文档

#### app.utils.http.JsonResponse

##### JsonResponse.\_\_init\_\_(self, data: dict=None, *, status: bool, message: str='', **kwargs)

项目自定义的 JsonResponse，规范化返回数据的格式，json格式如下：

```javascript
{
    "status": true,
    "data": {},
    "message": "",
}
```

data、status、message分别对应构造函数的参数，data在初始化的时候可以不指定

status则是必须参数，它表示请求的操作的执行状态，比如需要获取副本列表但是因为某些原因失败，则status应该为False。

message一般在请求的操作执行失败时给定，用来说明失败的原因

**注意：**status和message都是关键字参数

##### JsonResponse.add_value(key, value)

向data中添加一个键值对

##### 调用示例

```python
from app.utils.http import JsonResponse

response = JsonResponse(status=True, message='test')
response.add_value('key', 'value')
```

最后客户端收到的json数据为：

```javascript
{
	"status": true,
    "data": {
        "key": "value"
    },
    "message": "test",
}
```

