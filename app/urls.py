"""dccron URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [
    path('base/', views.base, name='base'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('exchange/', views.exchange, name='exchange'),
    path('exchangeinfo/<int:exid>', views.exchangeinfo, name='exchangeinfo'),
    path('symbollist/<int:exid>', views.symbollist, name='symbollist'),
    path('symbolupdate/<int:exid>', views.symbolupdate, name='symbolupdate'),
    path('symboladd/<int:exid>/<slug:symbol>', views.symboladd, name='symboladd'),
    path('symboldel/<int:exid>/<slug:symbol>', views.symboldel, name='symboldel'),
    path('symbol/', views.symbol, name='symbol'),

    path('symbolajax/<str:ecode>', views.symbolajax, name='symbolajax'),

]
