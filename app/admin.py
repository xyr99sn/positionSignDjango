from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('openid','name','std_id','sex','wx_nickname','wx_avatar','phone','academy','major','class_s')

@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ('name','introduction','start_time','end_time')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name','longitude','latitude','score','radius','transcript')
    readonly_fields = ("imageData",)

    def imageData(self, obj):
        return mark_safe(u'<img src="%s" width="100px" />' % obj.image.url)
    imageData.short_description = u'地点图片'

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('is_signed','score','time','created_time','user','position','transcript')