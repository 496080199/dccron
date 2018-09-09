
from django.shortcuts import render
from django.contrib import auth
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponse
import json
import ccxt
import re
from decimal import Decimal


from .form import *
from .models import *




from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

scheduler.start()


def writecastlog(cid,content):
    castlog = Castlog.objects.create(cast_id=cid)
    castlog.content = content
    castlog.save()

def timetoorder(exid,cid,symbol,amount,sellpercent):
    cast = Cast.objects.get(pk=cid)
    exchange = Exchange.objects.get(pk=exid)
    ex = eval("ccxt." + exchange.code + "()")
    ex.apiKey = exchange.apikey
    ex.secret = exchange.secretkey
    ex.options['createMarketBuyOrderRequiresPrice'] = False
    try:
        cost=cast.cost
        firstsymbol=symbol.split('_')[0]
        quatity=Decimal(ex.fetchbalance()[firstsymbol]['free'])
        orderbook = ex.fetch_order_book(symbol=symbol)
        bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        averageprice = Decimal((ask + bid) / 2)
        if averageprice*quatity > cost * (1+(sellpercent/100)):
            sellorderdata=exchange.create_market_sell_order(symbol=symbol, amount=quatity)
            if sellorderdata['info']['status'] == 'ok':
                content='定投收益已达到'+sellpercent+'%,成功卖出'
                writecastlog(cid,content)
    except:
        content = '定投卖出异常'
        writecastlog(cid, content)
        pass

    try:
        buyorderdata=ex.create_market_buy_order(symbol=symbol, amount=amount)
        if buyorderdata['info']['status'] == 'ok':
            cast.cost+=amount
            content = '定投成功买入'+str(amount)+'金额的'+str(symbol.split('_')[1])
            writecastlog(cid, content)
    except:
        content = '定投买入异常'
        writecastlog(cid, content)
        pass

####
def castaddorchange(request):
    cid=request.GET['cid']
    if cid:
        cast=Cast.objects.get(pk=cid)
        castform = CastForm(instance=cast)
    else:
        castform=CastForm()
    if request.method=='POST':
        pass
    return render(request, 'castinfo.html', {})
def castload(request,cid):
    cast=Cast.objects.get(pk=cid)
    job=scheduler.get_job(job_id=str(cid))
    if job:
        scheduler.reschedule_job("cron", id=str(cid), day=cast.day,hour=cast.hour, minute=cast.minute, second=0, kwargs={'exid': cast.exid,'cid':cid,'symbol':cast.symbol,'amount':cast.amount,'sellpercent':cast.sellpercent})
        job.resume()
        messages.add_message(request, messages.INFO, '任务' + cast.name + '重载成功')
    else:
        scheduler.add_job(timetoorder, "cron", id=str(cid), day=cast.day,hour=cast.hour, minute=cast.minute, second=0, kwargs={'exid': cast.exid,'cid':cid,'symbol':cast.symbol,'amount':cast.amount,'sellpercent':cast.sellpercent})
        messages.add_message(request, messages.INFO, '任务' + cast.name + '启动成功')
    register_events(scheduler)

    return redirect(reverse('cast', args=[]))
def castpause(request,cid):
    cast = Cast.objects.get(pk=cid)
    job = scheduler.get_job(job_id=str(cid))
    if job:
        job.pause()
        messages.add_message(request, messages.INFO, '任务' + cast.name + '已暂停')
    return redirect(reverse('cast', args=[]))
def castdel(request,cid):
    cast = Cast.objects.get(pk=cid)
    job = scheduler.get_job(job_id=str(cid))
    if job:
        cast.delete()
        job.remove()
    return redirect(reverse('cast', args=[]))
def cast(request):
    casts=Cast.objects.all()

    jobs=DjangoJob.objects.all()
    search = request.GET.get('search')
    if search:
        tmpcasts = []
        for cast in casts:
            if search in cast.name:
                tmpcasts.append(cast)
        casts = tmpcasts
    else:
        paginator = Paginator(casts, 20)
        page = request.GET.get('page')
        try:
            casts = paginator.page(page)
        except PageNotAnInteger:
            casts = paginator.page(1)
        except EmptyPage:
            casts = paginator.page(paginator.num_pages)


    return render(request, 'cast.html', {'casts':casts})

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
    usymbols = exchange.symbols
    search = request.GET.get('search')
    symbols = []
    if usymbols:
        usymbols=usymbols.split()

        for symbol in usymbols:
            symbol=re.sub('/','_',symbol)
            symbols.append(symbol)

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
    symbols=' '.join(ex.symbols)
    exchange.symbols=symbols
    exchange.save()
    return redirect(reverse('symbollist',args=[exid,]))

def symboladd(request,exid,symbol):
    exchange = Exchange.objects.get(pk=exid)
    esymbol=Symbol.objects.filter(name=symbol,exchange_id=exid)

    if esymbol.exists():
        messages.add_message(request, messages.INFO, exchange.name + str(symbol) + '交易对已存在')
    else:
        esymbol=Symbol.objects.create(name=symbol,exchange_id=exid)
        esymbol.save()
        messages.add_message(request, messages.INFO, exchange.name+str(symbol)+'交易对添加成功')


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


