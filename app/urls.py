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
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('passwd/', views.passwd, name='passwd'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('proxy/', views.proxy, name='proxy'),
    path('exchange/', views.exchange, name='exchange'),
    path('exchangeupdate/', views.exchangeupdate, name='exchangeupdate'),
    path('exchangeinfo/<int:exid>', views.exchangeinfo, name='exchangeinfo'),
    path('symbollist/<int:exid>', views.symbollist, name='symbollist'),
    path('symbolupdate/<int:exid>', views.symbolupdate, name='symbolupdate'),
    path('symboladd/<int:exid>/<slug:symbol>', views.symboladd, name='symboladd'),
    path('symboldel/<int:exid>/<slug:symbol>', views.symboldel, name='symboldel'),
    path('symbolclean/<int:exid>', views.symbolclean, name='symbolclean'),
    path('symbol/', views.symbol, name='symbol'),
    path('symbolselect/', views.symbolselect, name='symbolselect'),
    path('cast/', views.cast, name='cast'),
    path('castadd/', views.castadd, name='castadd'),
    path('castupdate/<int:cid>', views.castupdate, name='castupdate'),
    path('castdel/<int:cid>', views.castdel, name='castdel'),
    path('castload/<int:cid>', views.castload, name='castload'),
    path('castpause/<int:cid>', views.castpause, name='castpause'),
    path('castlog/<int:cid>', views.castlog, name='castlog'),
    path('cleancastlog/<int:cid>', views.cleancastlog, name='cleancastlog'),
    path('condition/', views.condition, name='condition'),
    path('getsymbolava/<int:exid>/<slug:symbol>', views.getsymbolava, name='getsymbolava'),
    path('getsymbolprice/<int:exid>/<slug:symbol>', views.getsymbolprice, name='getsymbolprice'),
    path('conditionadd/', views.conditionadd, name='conditionadd'),
    path('conditionupdate/<int:cid>', views.conditionupdate, name='conditionupdate'),
    path('conditiondel/<int:cid>', views.conditiondel, name='conditiondel'),
    path('conditionload/<int:cid>', views.conditionload, name='conditionload'),
    path('conditonpause/<int:cid>', views.conditionpause, name='conditionpause'),
    path('conditonlog/<int:cid>', views.conditionlog, name='conditionlog'),
    path('cleanconditonlog/<int:cid>', views.cleanconditionlog, name='cleanconditionlog'),




]
