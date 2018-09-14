from .models import *
import ccxt,re
from decimal import Decimal
import traceback

def writecastlog(cid,content):
    castlog = Castlog.objects.create(cast_id=cid)
    castlog.content = content
    castlog.save()

def casttoorder(cast,exchange):
    symbol = re.sub('_', '/', cast.symbol)
    ex = eval("ccxt." + exchange.code + "()")
    ex.apiKey = exchange.apikey
    ex.secret = exchange.secretkey
    ex.options['createMarketBuyOrderRequiresPrice'] = False
    ex.options['marketBuyPrice'] = False
    cast = Cast.objects.get(pk=cast.id)
    try:
        cost=cast.cost
        firstsymbol=symbol.split('/')[0]
        quatity=Decimal(ex.fetch_balance()[firstsymbol]['free'])
        orderbook = ex.fetch_order_book(symbol=symbol)
        bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        averageprice = Decimal((ask + bid) / 2)
        if averageprice*quatity > cost * (1+(cast.sellpercent/100)):
            sellorderdata=ex.create_market_sell_order(symbol=symbol, amount=str(quatity))
            if sellorderdata['info']['status'] == 'ok':
                content='定投收益已达到'+cast.sellpercent+'%,成功卖出'
                writecastlog(cast.id,content)
            else:
                content = '卖出单异常'
                writecastlog(cast.id, content)
    except:
        content = '定投卖出异常:'+traceback.format_exc()
        writecastlog(cast.id, content)
        pass

    try:
        amount=cast.amount
        buyorderdata=ex.create_market_buy_order(symbol=symbol, amount=str(amount),params={'cost':str(amount)})
        if buyorderdata['info']['status'] == 'ok':
            cast.cost+=amount
            cast.save()
            content = '定投成功买入'+str(amount)+'金额的'+str(symbol.split('/')[1])
            writecastlog(cast.id, content)
        else:
            content = '买入单异常'
            writecastlog(cast.id, content)
    except:

        content = '定投买入异常:'+traceback.format_exc()
        writecastlog(cast.id, content)
        pass


def writeconditionlog(cid,content):
    conditionlog = Conditionlog.objects.create(condition_id=cid)
    conditionlog.content = content
    conditionlog.save()

def scconditionstop(cid):
    jobid = 'condition' + str(cid)
    jobs = DjangoJob.objects.filter(name=jobid)
    if jobs.exists():
        jobs[0].delete()

def conditiontoorder(condition,exchange):
    symbol = re.sub('_', '/', condition.symbol)
    price=condition.price
    number=condition.number
    ex = eval("ccxt." + exchange.code + "()")
    ex.apiKey = exchange.apikey
    ex.secret = exchange.secretkey
    try:
        orderbook = ex.fetch_order_book(symbol=symbol)
        bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        averageprice = Decimal((ask + bid) / 2)
        if condition.direction =='sell':
            if averageprice > price:
                sellorderdata = ex.create_market_sell_order(symbol=symbol, amount=number)
                if sellorderdata['info']['status'] == 'ok':
                    content = '已达到价格为' + price + '条件,成功卖出'
                    writeconditionlog(condition.id, content)
                    scconditionstop(condition.id)
                else:
                    content = '卖出单异常'
                    writecastlog(condition.id, content)

        elif condition.direction == 'buy':
            if averageprice < price:
                buyorderdata = ex.create_market_buy_order(symbol=symbol, amount=number,price=averageprice)
                if buyorderdata['info']['status'] == 'ok':
                    content = '已按价格为' + averageprice + '条件,成功买入'
                    writeconditionlog(condition.id, content)
                    scconditionstop(condition.id)
                else:
                    content = '买入单异常'
                    writecastlog(condition.id, content)

    except:
        content = '交易异常' +traceback.format_exc()
        writeconditionlog(condition.id, content)
        pass
