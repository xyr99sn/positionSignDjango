from django.db import models
from django.utils import timezone


class User(models.Model):
    """
    用户表
    """

    # id 主键
    openid = models.CharField(verbose_name='openid', max_length=50, null=False)
    name = models.CharField(verbose_name='姓名', max_length=10, null=False)
    std_id = models.CharField(verbose_name='学号', max_length=20)
    sex = models.CharField(verbose_name='性别', max_length=4)
    wx_nickname = models.CharField(verbose_name='微信昵称', max_length=20)
    wx_avatar = models.CharField(verbose_name='头像链接', max_length=100)
    phone = models.CharField(verbose_name='电话', max_length=20)
    academy = models.CharField(verbose_name='学院', max_length=10)
    major = models.CharField(verbose_name='专业', max_length=10)
    class_s = models.CharField(verbose_name='班级', max_length=10)
    last_login = models.DateField(null=True, default=timezone.now)
    createTime = models.DateField(null=True)
    is_bind = models.BooleanField(default=False)


class Transcript(models.Model):
    """
    副本表
    """

    # id 主键 int 默认创建
    name = models.CharField(verbose_name='副本名', max_length=10, null=False)
    introduction = models.CharField(verbose_name='副本介绍', max_length=200, null=False)
    start_time = models.DateTimeField(verbose_name='副本开始时间')
    end_time = models.DateTimeField(verbose_name='副本结束时间')
    number = models.IntegerField(verbose_name='参与人数', default=0)
    icon = models.CharField(verbose_name='副本图标', max_length=100, null=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    """
    地点表
    """

    # id 主键 int 默认创建
    name = models.CharField(verbose_name='地点名', max_length=10, null=False)
    longitude = models.FloatField(verbose_name='经度', null=False)
    latitude = models.FloatField(verbose_name='纬度', null=False)
    score = models.IntegerField(verbose_name='初始分值')
    radius = models.IntegerField(verbose_name='打卡半径')
    introduction = models.CharField(verbose_name='介绍文案', max_length=500)
    image = models.CharField(verbose_name="图片", max_length=100)
    is_used = models.BooleanField(default=False)
    # 外键 删除时置NULL
    transcript = models.ForeignKey(verbose_name='所属副本', to=Transcript, related_name='position', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Record(models.Model):
    """
    签到记录
    """

    # id 主键
    is_signed = models.BooleanField(verbose_name='是否签到成功', null=False)
    score = models.FloatField(verbose_name='分值', null=False)
    time = models.DateTimeField(verbose_name='签到时间', null=False)
    created_time = models.DateTimeField(verbose_name='创建时间', auto_now=True)
    # 外键
    user = models.ForeignKey(verbose_name='用户', to=User, related_name='record', on_delete=models.CASCADE)
    position = models.ForeignKey(verbose_name='签到地点', to=Position, related_name='record', on_delete=models.SET_NULL, null=True)
    transcript = models.ForeignKey(verbose_name='所属副本', to=Transcript, related_name='record', on_delete=models.SET_NULL, null=True)


class Message(models.Model):
    """
    留言记录
    """
    # id 主键
    content = models.CharField(verbose_name='留言内容', null=False, max_length=255)
    time = models.DateTimeField(verbose_name='留言时间', null=False)
    # 外键
    user = models.ForeignKey(verbose_name='用户', to=User, related_name='message', on_delete=models.CASCADE)
    position = models.ForeignKey(verbose_name='地点', to=Position, related_name='message', on_delete=models.SET_NULL, null=True)


class Join(models.Model):
    """
    参加活动记录
    """
    # id 主键
    time = models.DateTimeField(verbose_name='参加时间', null=False)
    # 外键
    user = models.ForeignKey(verbose_name='用户', to=User, related_name='join', on_delete=models.CASCADE)
    transcript = models.ForeignKey(verbose_name='活动', to=Transcript, related_name='join', on_delete=models.SET_NULL, null=True)
