
from django.shortcuts import render
from django.contrib import auth
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
import json
import ccxt

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
    exchange=Exchange.objects.get(pk=exid)
    exchangeform=ExchangeForm(instance=exchange)

    return render(request, 'exchangeinfo.html', {'exchangeform':exchangeform})

def symbollist(request,exid):
    exchange = Exchange.objects.get(pk=exid)
    symbols=exchange.symbols.split()
    paginator = Paginator(symbols, 20)
    page = request.GET.get('page')
    try:
        symbols = paginator.page(page)
    except PageNotAnInteger:
        symbols = paginator.page(1)
    except EmptyPage:
        symbols = paginator.page(paginator.num_pages)

    return render(request, 'symbollist.html', {'exid':exid,'symbols': symbols})


def symbolupdate(request,exid):
    exchange = Exchange.objects.get(pk=exid)
    ex=eval("ccxt."+exchange.code+"()")
    ex.load_markets()
    exchange.symbols=ex.symbols
    exchange.save()
    return redirect(reverse('symbollist',args=[exid,]))


def symbol(request):
    exchanges = Exchange.objects.all().values('id','name')

    return render(request, 'symbol.html',{'exchanges':exchanges})



def symbolajax(request,ecode):
    symbol=Symbol.objects.filter(ecode__exact=ecode)[0]
    return HttpResponse(json.dumps(symbol.snames), content_type='application/json')


