from .models import *
import ccxt, re
from decimal import Decimal
import traceback


def writecastlog(cid, content):
    castlog = Castlog.objects.create(cast_id=cid)
    castlog.content = content
    castlog.save()


def casttoorder(cast, exchange):
    symbol = re.sub('_', '/', cast.symbol)
    ex = eval("ccxt." + exchange.code + "()")
    ex.apiKey = exchange.apikey
    ex.secret = exchange.secretkey
    ex.options['createMarketBuyOrderRequiresPrice'] = False
    ex.options['marketBuyPrice'] = False
    cast = Cast.objects.get(pk=cast.id)
    cost = Decimal(cast.cost)
    firstsymbol = symbol.split('/')[0]
    try:
        quatity = Decimal(ex.fetch_balance()[firstsymbol]['free'])
        orderbook = ex.fetch_order_book(symbol=symbol)
        bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        averageprice = Decimal((ask + bid) / 2)
        currentvalue = averageprice * quatity
        if cost == 0.0 and quatity != 0.0:
            cast.cost = currentvalue
            cast.save()
        if currentvalue > cost * Decimal(1 + (cast.sellpercent / 100)):
            sellorderdata = ex.create_market_sell_order(symbol=symbol, amount=str(quatity))
            if sellorderdata['info']['status'] == 'ok':
                content = '定投收益已达到' + str(cast.sellpercent) + '%,成功卖出'
                writecastlog(cast.id, content)
            else:
                content = '卖出单异常:' + sellorderdata['info']['status']
                writecastlog(cast.id, content)
    except:
        content = '卖出单异常:' + traceback.format_exc()
        writecastlog(cast.id, content)

    try:
        amount = Decimal(cast.amount)
        buyorderdata = ex.create_market_buy_order(symbol=symbol, amount=str(amount), params={'cost': str(amount)})
        if buyorderdata['info']['status'] == 'ok':
            cast.cost += amount
            cast.save()
            content = '定投成功买入' + str(amount) + '金额的' + str(symbol.split('/')[1])
            writecastlog(cast.id, content)
        else:
            content = '买入单异常:' + buyorderdata['info']['status']
            writecastlog(cast.id, content)
    except:
        content = '买入单异常:' + traceback.format_exc()
        writecastlog(cast.id, content)


def writeconditionlog(cid, content):
    conditionlog = Conditionlog.objects.create(condition_id=cid)
    conditionlog.content = content
    conditionlog.save()


def scconditionstop(cid):
    jobid = 'condition' + str(cid)
    jobs = DjangoJob.objects.filter(name=jobid)
    if jobs.exists():
        jobs[0].delete()


def conditiontoorder(condition, exchange):
    try:
        symbol = re.sub('_', '/', condition.symbol)
        price = condition.price
        number = condition.number
        ex = eval("ccxt." + exchange.code + "()")
        ex.apiKey = exchange.apikey
        ex.secret = exchange.secretkey
        orderbook = ex.fetch_order_book(symbol=symbol)
        bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        averageprice = Decimal((ask + bid) / 2)
        if condition.direction == 'sell' and averageprice > price:
            sellorderdata = ex.create_market_sell_order(symbol=symbol, amount=str(number))
            if sellorderdata['info']['status'] == 'ok':
                content = '已按价格为' + str(price) + '条件下单卖出'
                writeconditionlog(condition.id, content)
                scconditionstop(condition.id)
            else:
                content = '卖出单异常'
                writecastlog(condition.id, content)

        elif condition.direction == 'buy' and averageprice < price:
            buyorderdata = ex.create_market_buy_order(symbol=symbol, amount=str(number), params={'price':str(averageprice)})
            if buyorderdata['info']['status'] == 'ok':
                content = '已按价格为' + str(averageprice) + '条件下单买入'
                writeconditionlog(condition.id, content)
                scconditionstop(condition.id)
            else:
                content = '买入单异常'
                writecastlog(condition.id, content)
        else:
            content = '未满足下单条件'
            writecastlog(condition.id, content)

    except:
        content = '条件投异常' + traceback.format_exc()
        writeconditionlog(condition.id, content)