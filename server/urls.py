"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from app.views import *
from django.views.static import serve
from .settings import MEDIA_ROOT

urlpatterns = [
    path('app/admin/', admin.site.urls),

    re_path(r'^photos/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    re_path(r'^app/login', loginUser),
    re_path(r'^app/getUserInfo', getUserInfo),
    re_path(r'^app/register$', register),
    re_path(r'^app/getTranscriptList$', getTranscriptList),
    re_path(r'^app/getPositionList$', getPositionList),
    re_path(r'^app/getScoreOrder', getScoreOrder),
    re_path(r'^app/sign$', addRecord),
    re_path(r'^app/backendIndex$', backendIndex),
    re_path(r'^app/backendUser', backendUser),
    re_path(r'^app/backendGetActivity', backendGetActivity),
    re_path(r'^app/backendGetFreePosition', backendGetFreePosition),
    re_path(r'^app/backendGetAllPosition', backendGetAllPosition),
    re_path(r'^app/backendGetSign', backendGetSign),
    re_path(r'^app/backendAddActivity', backendAddActivity),
    re_path(r'^app/backendAddPosition', backendAddPosition),
    # re_path(r'^app/backendDeletePosition', backendDeletePosition),
]

