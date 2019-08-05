from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from . import views


urlpatterns = [
    path("my",                  views.my,       name="my"),
    path("send",                views.send,     name="send"),
    path('view/<int:batch_id>', views.view,     name='view'),
    path("public",              views.public,   name="public"),
    path("",                    views.home,     name="home"),
]
