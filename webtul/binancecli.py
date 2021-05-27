#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" For Binance.com
Hand made client could be easy extend
"""
__author__ = 'Zagfai'
__date__ = '2020-12'

import time
import hmac
import logging
import hashlib
import requests
import socket
import websocket
import threading
import queue
from urllib.parse import urljoin
from decimal import Decimal


class Client():
    endpoint = 'https://api.binance.com'
    proxies = None
    timeout = 60
    api_key = ""
    api_secret = ""
    s = None

    def __init__(self, k, s, proxy={'https': 'socks5://127.0.0.1:1080'}, timeout=60):
        self.api_key = k
        self.api_secret = s
        self.proxies = proxy
        self.timeout = timeout

        self.s = requests.Session()
        self.s.headers.update({"X-MBX-APIKEY": self.api_key})
        if self.proxies:
            self.s.proxies.update(self.proxies)

    def _sign_queries(self, queries: dict = None):
        if queries is None:
            queries = {}
        qstr = '&'.join(['='.join([str(k), str(v)]) for k, v in queries.items()])
        quote_qstr = '&'.join(['='.join([str(k), str(v)]) for k, v in queries.items()])
        timestamp = str(int(time.time() * 1000))
        if qstr != '':
            qstr += '&'
            quote_qstr += '&'
        qstr += 'timestamp=%s' % timestamp
        quote_qstr += 'timestamp=%s' % timestamp
        sign = hmac.new(bytes(self.api_secret, 'utf8'), bytes(qstr, 'utf8'), hashlib.sha256).hexdigest()
        quote_qstr += '&signature=%s' % sign
        logging.debug(quote_qstr)
        return '?' + quote_qstr

    def reqget(self, uri, queries=None, no_sign=False):
        url = urljoin(self.endpoint, uri)
        if no_sign:
            if queries:
                quote_qstr = '&'.join(['='.join([str(k), str(v)]) for k, v in queries.items()])
                url = url + '?' + quote_qstr
        else:
            url = url + self._sign_queries(queries)
        req = self.s.get(url, timeout=self.timeout)
        return req.json()

    def reqpost(self, uri, queries=None, no_sign=False):
        url = urljoin(self.endpoint, uri)
        if not no_sign:
            url = url + self._sign_queries(queries)
        req = self.s.post(url, timeout=self.timeout)
        return req.json()

    def get_server_status(self):
        res = self.reqget("/wapi/v3/systemStatus.html")
        return True if (res.get('status', None) == 0) else False

    def get_server_info(self):
        return self.reqget("/api/v3/exchangeInfo", no_sign=True)

    def get_prices(self, pair=None):
        respdata = self.reqget("/api/v3/ticker/price", no_sign=True)
        return {i['symbol']: Decimal(i['price']) for i in respdata}

    def get_wallet(self, prices=None):
        wallet = {}

        res = self.reqget('/api/v3/account')
        if 'balances' not in res:
            logging.error(res)
        account = res['balances']
        account = {i['asset']: Decimal(i['free']) for i in account if float(i['free']) > 0}
        wallet['holdings'] = account

        if not prices:
            prices = self.get_prices()

        spot_in_usd = {i: prices[i+'USDT'] * account[i]
                       for i in account if not i.endswith('USDT') and i+'USDT' in prices}
        land_in_usd = {i.lstrip('LD'): prices[i.lstrip('LD')+'USDT'] * account[i]
                       for i in account
                       if i.startswith('LD') and not i.endswith('USDT') and i.lstrip('LD')+'USDT' in prices}
        wallet['spot'] = spot_in_usd
        wallet['spot']['USDT'] = account.get('USDT', 0)
        wallet['land'] = land_in_usd
        wallet['land']['USDT'] = account.get('LDUSDT', 0)

        liquid_amount = Decimal(0)
        res = self.reqget('/sapi/v1/bswap/liquidity')
        if type(res) == list:
            for liq in res:
                # only sum USD ( USDT BUSD DAI ) now
                asset = liq.get('share', {}).get('asset')
                liquid_amount += Decimal(asset.get('DAI', 0)) +\
                    Decimal(asset.get('USDT', 0)) +\
                    Decimal(asset.get('BUSD', 0)) +\
                    Decimal(asset.get('USDC', 0))
        wallet['liquid_USD'] = liquid_amount

        spot_land = sum(wallet['spot'].values()) + sum(wallet['land'].values())
        wallet['amount'] = spot_land + wallet['liquid_USD']

        return wallet

    def get_liq_pools(self):
        uri = '/sapi/v1/bswap/pools'
        return self.reqget(uri)

    def get_liq(self, pid=None):
        uri = '/sapi/v1/bswap/liquidity'
        # return self.reqget(uri, {"pollId": pid})
        return self.reqget(uri)

    def land_daily_product(self):
        return self.reqget('/sapi/v1/lending/daily/product/list', {"status": "SUBSCRIBABLE"})

    def land_all_products(self):
        return self.reqget('/sapi/v1/lending/project/list', {"type": "ACTIVITY"})

    def land_withdraw(self, coin, amount):
        res = self.reqget("/sapi/v1/lending/daily/token/position", {"asset": coin})
        logging.debug(res)
        if res:
            asset = res[0]
            pid = asset['productId']
            if Decimal(asset['freeAmount']) < amount:
                raise Exception("Insufficient Funds")

            try:
                res = self.land_daily_product()
                min_purchase_amount = Decimal([i for i in res if i['asset'] == coin][0]['minPurchaseAmount'])
                if amount < min_purchase_amount:
                    amount = min_purchase_amount
            except Exception as e:
                logging.warn("Get min_purchase_amount error. Do not try to reset min amount. %s" % str(e))

            res = self.reqpost("/sapi/v1/lending/daily/redeem",
                               {"productId": pid, "amount": amount, "type": 'FAST'})
            return res
        else:
            raise Exception("Funds Not Found")

    def land_deposit(self, product_id, amount):
        return self.reqpost('/sapi/v1/lending/daily/purchase', {"productId": product_id, "amount": amount})

    def trade(self, target, base, amount, prices=None):
        if base != 'USDT':
            if not prices:
                prices = self.get_prices()
            if target + base in prices:
                symbol = target + base
            elif base + target in prices:
                symbol = base + target
                target, base = base, target
                amount = - amount
            else:
                raise Exception("Do not find trade pair: %s %s" % (target, base))
            amount /= prices[base+'USDT']
        else:
            symbol = target + base

        orderparams = {
                'symbol': symbol,
                'side': 'BUY' if amount > 0 else 'SELL',
                'type': 'MARKET',
                'quoteOrderQty': abs(round(amount, 8))
                }
        return self.reqpost('/api/v3/order', orderparams)

    def klines(self, target, base='USDT', interval='5m', limit=500, endtime=None, starttime=None):
        reqdict = {"symbol": target+base, "interval": interval}
        if endtime and starttime:
            reqdict["startTime"] = starttime
            reqdict["endTime"] = endtime
        else:
            reqdict["limit"] = limit
        res = self.reqget(
                "/api/v3/klines",
                reqdict,
                no_sign=True)
        return res


class FutureClient(Client):
    endpoint = "https://fapi.binance.com"
    wws = "wss://fstream.binance.com"

    def ping(self):
        url = '/fapi/v1/ping'
        return self.reqget(url, no_sign=True) == {}

    def time(self):
        url = '/fapi/v1/time'
        return self.reqget(url, no_sign=True), int(time.time()*1000)

    def info(self):
        url = '/fapi/v1/exchangeInfo'
        return self.reqget(url, no_sign=True)

    def balance(self):
        url = '/fapi/v2/balance'
        return self.reqget(url)

    def account(self):
        url = "/fapi/v2/account"
        return self.reqget(url)

    def klines(self, target, base='USDT', interval='5m', limit=500, starttime=None, endtime=None):
        url = '/fapi/v1/continuousKlines'
        reqdict = {"pair": target+base, "interval": interval, "contractType": "PERPETUAL"}
        if endtime and starttime:
            reqdict["startTime"] = starttime
            reqdict["endTime"] = endtime
        reqdict["limit"] = limit
        res = self.reqget(url, reqdict, no_sign=True)
        return res

    def market_stream(self, targets, interval='1m', read_timeout=15):
        if len(targets) > 10:
            raise Exception("Too many stream targets")
        data_q = queue.Queue()

        def stream_thread():
            streams = '/'.join([f'{i}usdt_perpetual@continuousKline_1m' for i in targets])
            url = f'{self.wws}/stream?streams={streams}'
            ws = websocket.WebSocket()
            if self.proxies.get('https'):
                {'https': 'socks5://127.0.0.1:1080'}
                pxy = self.proxies.get('https')
                args = {
                        'http_proxy_host': pxy[pxy.rfind('/')+1: pxy.rfind(':')],
                        'http_proxy_port': int(pxy[pxy.rfind(':')+1:]),
                        'proxy_type': pxy[:pxy.find(':')],
                }
            ws.connect(url,
                       timeout=read_timeout,
                       ** args,
                       sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),))
            logging.info("Connected market data websocket.")
            while True:
                try:
                    data_q.put(ws.recv())
                except websocket._exceptions.WebSocketTimeoutException:
                    logging.info("Unexpected WebSocket Read Timeout, Thread will ended.")
                    break
            ws.close()

        thread = threading.Thread(target=stream_thread)
        thread.daemon = True
        thread.start()

        return thread, data_q

    def leverage(self, symbol, lever=2):
        url = '/fapi/v1/leverage'
        return self.reqpost(url, {'symbol': symbol, 'leverage': lever})

    def margin_isolated(self, symbol, isolated=False):
        url = '/fapi/v1/marginType'
        return self.reqpost(url, {'symbol': symbol, 'marginType': "ISOLATED" if isolated else "CROSSED"})

    def order(self, **args):
        url = '/fapi/v1/order'
        return self.reqpost(url, args)

    def position(self, symbol):
        url = '/fapi/v1/positionRisk'
        return self.reqget(url, {"symbol": symbol})


if __name__ == "__main__":
    import yaml
    CFG = yaml.safe_load(open('/etc/binance.yml'))
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
    # c = Client(CFG['trades'][0]['apikey'], CFG['trades'][0]['secret'])
    # print(c.get_server_status())
    # print(c.klines("BTC", interval='4h', limit=5))
    # print([(i['poolId'], i['poolName']) for i in c.get_liq_pools() if 'USDT' in i['poolName']])
    # print(c.get_liq(2))
    # print(str(c.get_server_info())[:200])
    # print(str(c.get_prices())[:200])
    # # print(c._sign_queries())
    # print(c.get_wallet())
    # print(str(c.land_daily_product())[:200])
    # print(str(c.land_all_products())[:200])
    # print(c.land_withdraw("USDT", Decimal('0.00234567890123')))
    # print(c.trade("BNB", "USDT", Decimal('-0.1234567890')))
    c = FutureClient(CFG['trades'][0]['apikey'], CFG['trades'][0]['secret'])
    import pprint
    pprint.pprint(c.position('BTCUSDT'))
    # pprint.pprint(c.balance())
    # pprint.pprint(c.leverage('BTCUSDT', 125))
    # pprint.pprint(c.margin_isolated('BTCUSDT', True))
    # pprint.pprint(c.order(symbol="BTCUSDT", side='BUY', type='MARKET', reduceOnly="TRUE",
    #                       quantity=0.001, newOrderRespType="RESULT"))
