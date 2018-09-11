from .models import *
import re
from decimal import Decimal

def writecastlog(cid,content):
    castlog = Castlog.objects.create(cast_id=cid)
    castlog.content = content
    castlog.save()

def timetoorder(exid,cid,symbol,amount,sellpercent):
    symbol = re.sub('_', '/', symbol)
    cast = Cast.objects.get(pk=cid)
    exchange = Exchange.objects.get(pk=exid)
    ex = eval("ccxt." + exchange.code + "()")
    ex.apiKey = exchange.apikey
    ex.secret = exchange.secretkey
    ex.options['createMarketBuyOrderRequiresPrice'] = False
    try:
        cost=cast.cost
        firstsymbol=symbol.split('/')[0]
        quatity=Decimal(ex.fetch_balance()[firstsymbol]['free'])
        orderbook = ex.fetch_order_book(symbol=symbol)
        bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        averageprice = Decimal((ask + bid) / 2)
        if averageprice*quatity > cost * (1+(sellpercent/100)):
            sellorderdata=exchange.create_market_sell_order(symbol=symbol, amount=quatity)
            if sellorderdata['info']['status'] == 'ok':
                content='定投收益已达到'+sellpercent+'%,成功卖出'
                writecastlog(cid,content)
    except Exception as e:
        content = '定投卖出异常:'+str(e)
        writecastlog(cid, content)
        pass

    try:
        buyorderdata=ex.create_market_buy_order(symbol=symbol, amount=amount)
        if buyorderdata['info']['status'] == 'ok':
            cast.cost+=amount
            content = '定投成功买入'+str(amount)+'金额的'+str(symbol.split('/')[1])
            writecastlog(cid, content)
    except Exception as e:
        content = '定投买入异常'+str(e)
        writecastlog(cid, content)
        pass
