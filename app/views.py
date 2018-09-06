
from django.shortcuts import render
from django.contrib import auth
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.contrib import messages
import json
import ccxt
import re

from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponse

from .form import *
from .models import *


# Create your views here.

def base(request):
    return render(request, 'base.html')

def login(request):
    if request.user.is_authenticated:
        return redirect(reverse('app.views.dashboard', args=[]))
    if request.method == 'POST':
        loginform=LoginForm(request.POST)
        if loginform.is_valid():
            logininfo=loginform.cleaned_data
            username=logininfo['username']
            password=logininfo['password']
            user=auth.authenticate(username=username,password=password)
            if user is not None and user.is_active:
                auth.login(request,user)

                return redirect(reverse('app.views.dashboard',args=[]))
        else:
            return render(request, 'login.html', {'loginform': loginform})
    loginform=LoginForm()
    return render(request, 'login.html',{'loginform':loginform})

def dashboard(request):
    return render(request, 'dashboard.html', {})

def exchange(request):
    exchanges=Exchange.objects.all()

    return render(request, 'exchange.html', {'exchagnes':exchanges})

def exchangeinfo(request,exid):
    exchange = Exchange.objects.get(pk=exid)
    exchangeform = ExchangeForm(instance=exchange)
    if request.method == 'POST':
        exchangeform=ExchangeForm(request.POST)
        if exchangeform.is_valid():
            exchangeinfo = exchangeform.cleaned_data
            exchange.apikey=exchangeinfo['apikey']
            exchange.secretkey=exchangeinfo['secretkey']
            exchange.status=exchangeinfo['status']
            exchange.save()
            messages.add_message(request,messages.INFO,'修改成功')


    return render(request, 'exchangeinfo.html', {'exchangeform':exchangeform,'exid':exid})

def symbollist(request,exid):
    exchange = Exchange.objects.get(pk=exid)
    usymbols=exchange.symbols.split()
    symbols=[]
    for symbol in usymbols:
        symbol=re.sub('/','_',symbol)
        symbols.append(symbol)
    search = request.GET.get('search')
    if search:
        tmpsymbols = []
        for symbol in symbols:
            if search.upper() in symbol:
                tmpsymbols.append(symbol)
        symbols = tmpsymbols
    else:
        paginator = Paginator(symbols, 20)
        page = request.GET.get('page')
        try:
            symbols = paginator.page(page)
        except PageNotAnInteger:
            symbols = paginator.page(1)
        except EmptyPage:
            symbols = paginator.page(paginator.num_pages)

    return render(request, 'symbollist.html', {'exchange':exchange,'symbols': symbols,'search':search})


def symbolupdate(request,exid):
    exchange = Exchange.objects.get(pk=exid)
    ex=eval("ccxt."+exchange.code+"()")
    ex.load_markets()
    exchange.symbols=ex.symbols
    exchange.save()
    return redirect(reverse('symbollist',args=[exid,]))

def symboladd(request,exid,symbol):
    exchange = Exchange.objects.get(pk=exid)
    symbol=Symbol.objects.get_or_create(name=symbol,exchange_id=exid)[0]
    symbol.save()
    messages.add_message(request, messages.INFO, exchange.name+symbol.name+'交易对添加成功')


    return redirect(reverse('symbollist', args=[exid, ]))

def symboldel(request,exid,symbol):
    exchange = Exchange.objects.get(pk=exid)
    symbol = Symbol.objects.get_or_create(name=symbol, exchange_id=exid)[0]
    symbol.delete()
    messages.add_message(request, messages.INFO, exchange.name + symbol.name + '交易对删除成功')
    return redirect(reverse('symbol', args=[ ]))



def symbol(request):
    exchanges = Exchange.objects.all().values('id','name')
    symbols=Symbol.objects.all()

    select = request.GET.get('select')
    if select:
        symbols=Symbol.objects.filter(exchange_id=select)
    else:
        paginator = Paginator(symbols, 20)
        page = request.GET.get('page')
        try:
            symbols = paginator.page(page)
        except PageNotAnInteger:
            symbols = paginator.page(1)
        except EmptyPage:
            symbols = paginator.page(paginator.num_pages)




    return render(request, 'symbol.html',{'exchanges':exchanges,'symbols':symbols})



def symbolajax(request,ecode):
    symbol=Symbol.objects.filter(ecode__exact=ecode)[0]
    return HttpResponse(json.dumps(symbol.snames), content_type='application/json')


