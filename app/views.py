
from django.shortcuts import render
from django.contrib import auth
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from pytz import timezone
import json,platform




from .form import *
from .models import *
from .trade import *




from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

tz=timezone('Asia/Shanghai')

scheduler = BackgroundScheduler(timezone=tz)
scheduler.add_jobstore(DjangoJobStore(), "default")

scheduler.start()





# Create your views here.


def login(request):
    if request.user.is_authenticated:
        return redirect(reverse('dashboard', args=[]))
    if request.method == 'POST':
        loginform=LoginForm(request.POST)
        if loginform.is_valid():
            logininfo=loginform.cleaned_data
            username=logininfo['username']
            password=logininfo['password']
            user=auth.authenticate(username=username,password=password)
            if user is not None and user.is_active:
                auth.login(request,user)

                return redirect(reverse('dashboard',args=[]))
            else:
                messages.add_message(request, messages.INFO, '用户名或密码不正确')
        else:
            return render(request, 'login.html', {'loginform': loginform})
    loginform=LoginForm()
    return render(request, 'login.html',{'loginform':loginform})
@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse('login', args=[]))

@login_required
def passwd(request):
    if request.method == 'POST':
        passwdform=PasswdForm(request.POST)
        if passwdform.is_valid():
            user=request.user
            passwdinfo = passwdform.cleaned_data
            oldpass = passwdinfo['oldpass']
            newpass = passwdinfo['newpass']
            rnewpass = passwdinfo['rnewpass']
            if check_password(oldpass,user.password):
                if newpass == rnewpass:
                    user.set_password(newpass)
                    user.save()
                    messages.add_message(request, messages.INFO, '密码修改成功,请重新登录')
                    return redirect(reverse('dashboard', args=[]))
                else:
                    messages.add_message(request, messages.INFO, '密码不一致')
            else:
                messages.add_message(request, messages.INFO, '旧密码不正确')

    passwdform=PasswdForm()

    return render(request, 'passwd.html', {'passwdform':passwdform})

@login_required
def dashboard(request):
    exchangecount=Exchange.objects.filter(status=1).count()
    symbolcount=Symbol.objects.all().count()
    castcount=Cast.objects.all().count()
    conditioncount=Condition.objects.all().count()
    system={}
    system['plateform']=platform.platform()
    system['machine']=platform.machine()
    system['arch'] = platform.architecture()[0]
    system['python']=platform.python_version()


    return render(request, 'dashboard.html', {'exchangecount':exchangecount,'symbolcount':symbolcount,'castcount':castcount,'conditioncount':conditioncount,'system':system})

@login_required
def exchange(request):
    exchanges=Exchange.objects.all().order_by('-status')
    search = request.GET.get('search')
    if search:
        exchanges=Exchange.objects.filter(Q(code__contains=search)|Q(name__contains=search))
    else:
        paginator = Paginator(exchanges, 20)
        page = request.GET.get('page')
        try:
            exchanges = paginator.page(page)
        except PageNotAnInteger:
            exchanges = paginator.page(1)
        except EmptyPage:
            exchanges = paginator.page(paginator.num_pages)

    return render(request, 'exchange.html', {'exchagnes':exchanges})

@login_required
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
            messages.add_message(request,messages.INFO,exchange.name+'交易所修改成功')
            return redirect(reverse('exchange', args=[]))


    return render(request, 'exchangeinfo.html', {'exchangeform':exchangeform,'exid':exid})

@login_required
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

@login_required
def symbolupdate(request,exid):
    exchange = Exchange.objects.get(pk=exid)
    ex=eval("ccxt."+exchange.code+"()")
    ex.apiKey = exchange.apikey
    ex.secret = exchange.secretkey
    ex.load_markets()
    symbols=' '.join(ex.symbols)
    exchange.symbols=symbols
    exchange.save()
    return redirect(reverse('symbollist',args=[exid,]))

@login_required
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

@login_required
def symboldel(request,exid,symbol):
    exchange = Exchange.objects.get(pk=exid)
    symbol = Symbol.objects.get_or_create(name=symbol, exchange_id=exid)[0]
    symbol.delete()
    messages.add_message(request, messages.INFO, exchange.name + symbol.name + '交易对删除成功')
    return redirect(reverse('symbol', args=[ ]))


@login_required
def symbol(request):
    exchanges = Exchange.objects.all().values('id','name')
    symbols=Symbol.objects.all().order_by('name')

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

@csrf_exempt
@login_required
def symbolselect(request):
    selectlist=[]
    exchanges=Exchange.objects.filter(status=1)
    for exchange in exchanges:
        exchangedict={}
        exchangedict['name']=str(exchange.name)
        exchangedict['value']=str(exchange.id)
        symbols=Symbol.objects.filter(exchange_id=exchange.id)
        tmpsymbols=[]
        for symbol in symbols:
            symboldict={}
            symboldict['name']=str(symbol.name)
            symboldict['value']=str(symbol.name)
            tmpsymbols.append(symboldict)
        exchangedict['sub']=tmpsymbols
        selectlist.append(exchangedict)

    return HttpResponse(json.dumps(selectlist), content_type='application/json')


################################################
@login_required
def cast(request):
    casts=Cast.objects.all().order_by('-ttime')
    search = request.GET.get('search')
    if search:
        casts = Cast.objects.filter(name__contains=search)
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

@login_required
def castadd(request):
    castform = CastForm()
    if request.method=='POST':
        castform = CastForm(request.POST)
        if castform.is_valid():
            cast=castform.save(commit=False)
            cast.save()
            messages.add_message(request, messages.INFO, '定投任务' + cast.name + '已添加')
            return redirect(reverse('cast', args=[]))
    return render(request, 'castadd.html', {'castform':castform})
@login_required
def castupdate(request,cid):
    cast = Cast.objects.get(pk=cid)
    castform = CastForm(instance=cast)
    if request.method=='POST':
        castform = CastForm(request.POST)
        if castform.is_valid():
            castinfo = castform.cleaned_data
            cast.minute=castinfo['minute']
            cast.hour = castinfo['hour']
            cast.day = castinfo['day']
            cast.exid = castinfo['exid']
            cast.symbol = castinfo['symbol']
            cast.amount = castinfo['amount']
            cast.sellpercent = castinfo['sellpercent']
            cast.save()
            messages.add_message(request, messages.INFO, '任务' + cast.name + '修改成功')

            return redirect(reverse('cast', args=[]))

    return render(request, 'castupdate.html', {'castform': castform,'cid':cid})

@login_required
def castload(request,cid):
    cast=Cast.objects.get(pk=cid)
    exchange = Exchange.objects.get(pk=cast.exid)
    jobid='cast'+str(cid)
    job=scheduler.get_job(job_id=jobid)
    if job:
        job.remove()
        scheduler.add_job(casttoorder, "cron", id=jobid, day=cast.day, hour=cast.hour, minute=cast.minute, second=0,
                          kwargs={'cast': cast, 'exchange': exchange})

        messages.add_message(request, messages.INFO, '任务' + cast.name + '重载成功')
    else:
        scheduler.add_job(casttoorder, "cron", id=jobid, day=cast.day,hour=cast.hour, minute=cast.minute, second=0, kwargs={'cast': cast, 'exchange': exchange})
        messages.add_message(request, messages.INFO, '任务' + cast.name + '启动成功')
    register_events(scheduler)

    return redirect(reverse('cast', args=[]))
@login_required
def castpause(request,cid):
    cast = Cast.objects.get(pk=cid)
    jobid = 'cast' + str(cid)
    jobs = DjangoJob.objects.filter(name=jobid)
    if jobs.exists():
        jobs[0].delete()
        messages.add_message(request, messages.INFO, '任务' + cast.name + '已暂停')
    else:
        messages.add_message(request, messages.INFO, '任务' + cast.name + '处于暂停状态')
    return redirect(reverse('cast', args=[]))
@login_required
def castdel(request,cid):
    cast = Cast.objects.get(pk=cid)
    jobid = 'cast' + str(cid)
    name=cast.name
    job = scheduler.get_job(job_id=jobid)
    if job:
        job.remove()
    cast.delete()
    messages.add_message(request, messages.INFO, '任务' + name + '已删除')
    return redirect(reverse('cast', args=[]))

@login_required
def castlog(request,cid):
    castlogs=Castlog.objects.filter(cast_id=cid).order_by('-tltime')
    cast=Cast.objects.get(pk=cid)
    search = request.GET.get('search')

    if search:
        castlogs = Castlog.objects.filter(Q(content__contains=search)|Q(tltime__in=search))
    else:
        paginator = Paginator(castlogs, 20)
        page = request.GET.get('page')
        try:
            castlogs = paginator.page(page)
        except PageNotAnInteger:
            castlogs = paginator.page(1)
        except EmptyPage:
            castlogs = paginator.page(paginator.num_pages)


    return render(request, 'castlog.html', {'castlogs': castlogs,'cast':cast})

@login_required
def condition(request):
    conditions=Condition.objects.all().order_by('-ttime')
    search = request.GET.get('search')
    if search:
        conditions=Condition.objects.filter(name__contains=search)
    else:
        paginator = Paginator(conditions, 20)
        page = request.GET.get('page')
        try:
            conditions = paginator.page(page)
        except PageNotAnInteger:
            conditions = paginator.page(1)
        except EmptyPage:
            conditions = paginator.page(paginator.num_pages)


    return render(request, 'condition.html', {'conditions':conditions})

@login_required
def conditionadd(request):
    conditionform = ConditionForm()
    if request.method=='POST':
        conditionform = ConditionForm(request.POST)
        if conditionform.is_valid():
            condition=conditionform.save(commit=False)
            condition.save()
            messages.add_message(request, messages.INFO, '条件投任务' + condition.name + '已添加')
            return redirect(reverse('condition', args=[]))

    return render(request, 'conditionadd.html', {'conditionform':conditionform})
@login_required
def conditionupdate(request,cid):
    condition = Condition.objects.get(pk=cid)
    conditionform = ConditionForm(instance=condition)
    if request.method=='POST':
        conditionform = ConditionForm(request.POST)
        if conditionform.is_valid():
            conditioninfo = conditionform.cleaned_data
            condition.exid = conditioninfo['exid']
            condition.symbol = conditioninfo['symbol']
            condition.direction = conditioninfo['direction']
            condition.number = conditioninfo['number']
            condition.price = conditioninfo['price']
            condition.save()
            messages.add_message(request, messages.INFO, '任务' + condition.name + '修改成功')

            return redirect(reverse('condition', args=[]))

    return render(request, 'conditionupdate.html', {'conditionform': conditionform,'cid':cid})
@login_required
def conditionload(request,cid):
    condition=Condition.objects.get(pk=cid)
    exchange = Exchange.objects.get(pk=condition.exid)
    jobid='condition'+str(cid)
    job=scheduler.get_job(job_id=jobid)
    if job:
        job.remove()
        scheduler.add_job(conditiontoorder, "cron", id=jobid, day='*', hour='*', minute='*', second=30,
                          kwargs={'condition': condition, 'exchange': exchange})

        messages.add_message(request, messages.INFO, '任务' + condition.name + '重载成功')
    else:
        scheduler.add_job(conditiontoorder, "cron", id=jobid, day='*', hour='*', minute='*', second=30,
                          kwargs={'condition': condition, 'exchange': exchange})
        messages.add_message(request, messages.INFO, '任务' + condition.name + '启动成功')
    register_events(scheduler)

    return redirect(reverse('condition', args=[]))
@login_required
def conditionpause(request,cid):
    condition = Condition.objects.get(pk=cid)
    jobid = 'condition' + str(cid)
    jobs = DjangoJob.objects.filter(name=jobid)
    if jobs.exists():
        jobs[0].delete()
        messages.add_message(request, messages.INFO, '任务' + condition.name + '已暂停')
    else:
        messages.add_message(request, messages.INFO, '任务' + condition.name + '处于暂停状态')
    return redirect(reverse('condition', args=[]))
@login_required
def conditiondel(request,cid):
    condition = Condition.objects.get(pk=cid)
    jobid = 'condition' + str(cid)
    name=condition.name
    job = scheduler.get_job(job_id=jobid)
    if job:
        job.remove()
    condition.delete()
    messages.add_message(request, messages.INFO, '任务' + name + '已删除')
    return redirect(reverse('condition', args=[]))
@login_required
def conditionlog(request,cid):
    conditionlogs=Conditionlog.objects.filter(condition_id=cid).order_by('-tltime')
    condition=Condition.objects.get(pk=cid)
    search = request.GET.get('search')

    if search:
        conditionlogs = Conditionlog.objects.filter(Q(content__contains=search) | Q(tltime__in=search))
    else:
        paginator = Paginator(conditionlogs, 20)
        page = request.GET.get('page')
        try:
            conditionlogs = paginator.page(page)
        except PageNotAnInteger:
            conditionlogs = paginator.page(1)
        except EmptyPage:
            conditionlogs = paginator.page(paginator.num_pages)


    return render(request, 'conditionlog.html', {'conditionlogs': conditionlogs,'condition':condition})