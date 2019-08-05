"""core URL Configuration

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
from django.urls import path, include
from django.conf.urls import url
from core import views as core_views
from batch import views as batch_views


urlpatterns = [
    path('admin/', admin.site.urls),

    # google, facebook auth
    url(r'^accounts/', include('allauth.urls')),

    # email login
    url(r'^signup/$', batch_views.signup, name='signup'),
    url(r'^activate_email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', batch_views.activate, name='activate_email'),

    # site
    path("my", core_views.my, name="my"),
    path("send", core_views.send, name="send"),
    path('view/<int:batch_id>', view=core_views.view),
    path("public", core_views.public, name="public"),
    path("", core_views.home, name="home"),
]
