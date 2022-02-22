## list of all markets
import json, requests # Install requests module first.
from pandas import json_normalize
import numpy as np
from time import sleep
import pandas as pd
from datetime import datetime
from dateutil import tz
import pprint, talib
import requests

url = "https://api.coindcx.com/exchange/v1/markets"

response = requests.get(url)
data = response.json()
#print(data)

url = "https://api.coindcx.com/exchange/v1/markets_details"

response = requests.get(url)
data = response.json()

df = json_normalize(data)

df = df.loc[df['coindcx_name'].isin(["AXSBTC", "MANABTC", "ENJBTC", "SANDBTC", "ERNBTC", "YGGBTC", "ALICEBTC", "ILVBTC"])]
pairs = df.pair.values
print(pairs)

bought_at = dict()

bought_qty = dict()

sold_at = dict()

pair_market = {'B-ENJ_BTC': 'ENJBTC', 'B-ILV_BTC': 'ILVBTC', 'B-ALICE_BTC':'ALICEBTC', 'B-SAND_BTC':'SANDBTC', 'B-YGG_BTC':'YGGBTC',
 'B-MANA_BTC':'MANABTC', 'B-AXS_BTC':'AXSBTC'}

key = "***"
secret = "***"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 68
RSI_OVERSOLD = 32

in_portfolio = list()
pnl = list()
pnlr = list()
last_closed_at = dict()
prof = dict()
investment = dict()
current = dict()

def rsi1m(tgCurrency, RSI_PERIOD):
    url = "https://public.coindcx.com/market_data/candles?pair=" + tgCurrency + "&interval=1m"
    response = requests.get(url)
    try:
        data = response.json()
        candle = json_normalize(data)
        candle["time"]= pd.to_datetime(candle["time"],unit='ms').\
                                                       dt.tz_localize('utc').\
                                                       dt.tz_convert('Asia/Kolkata')
        #print("started")
        np_closes = candle.sort_values(by=['time'], ascending=True).close.values
        close = np_closes[-1]
        rsi = talib.RSI(np_closes, RSI_PERIOD)
            #print("all rsis calculated so far")
            #print(rsi)
        last_rsi = rsi[-1]
            #print(candle[["close", "time"]].iloc[[0]])
        #print("the current rsi for " + pair + " is {}".format(last_rsi))
        return last_rsi, close
    except:
        return rsi1m(tgCurrency = tgCurrency, RSI_PERIOD = RSI_PERIOD)
    

    
def rsi4h(tgCurrency, RSI_PERIOD):
    url = "https://public.coindcx.com/market_data/candles?pair=" + tgCurrency + "&interval=2h"
    response = requests.get(url)
    try:
        data = response.json()
        candle = json_normalize(data)
        candle["time"]= pd.to_datetime(candle["time"],unit='ms').\
                                                       dt.tz_localize('utc').\
                                                       dt.tz_convert('Asia/Kolkata')
        #print("started")
        np_closes = candle.sort_values(by=['time'], ascending=True).close.values
        close = np_closes[-1]
        rsi = talib.RSI(np_closes, RSI_PERIOD)
            #print("all rsis calculated so far")
            #print(rsi)
        last_rsi = rsi[-1]
        second_last_rsi = rsi[-2]
            #print(candle[["close", "time"]].iloc[[0]])
            #print("the current rsi for " + pair + " is {}".format(last_rsi))
        trend = rsi > last_rsi
        print(rsi[494:500])
        #print((trend == True)[494:499])
        #print(np.where(trend == True)[-1])
        return sum((trend == True)[494:498]), last_rsi, second_last_rsi
    except:
        return rsi4h(tgCurrency = tgCurrency, RSI_PERIOD = RSI_PERIOD)
        
    

def isprofit(bought_at, bought_qty, close, tgCurrency, investment, current):
    investment[pair] = bought_at[pair]*bought_qty[pair]
    current[pair] = last_closed_at[pair]*bought_qty[pair]
    return round((current[pair] - investment[pair])*100/investment[pair],2)

def marketSell(tgCurrency, qty, key, secret):
    
    secret_bytes = bytes(secret, encoding='utf-8')


    # Generating a timestamp.
    timeStamp = int(round(time.time() * 1000))

    body = {
      "side": "sell",    
      "order_type": "market_order", 
      "market": tgCurrency, #pair_market[pair] 
      "total_quantity": qty, #bought_qty[pair]
      "timestamp": timeStamp
    }

    json_body = json.dumps(body, separators = (',', ':'))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    url = "https://api.coindcx.com/exchange/v1/orders/create"

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': key,
        'X-AUTH-SIGNATURE': signature
    }

    response = requests.post(url, data = json_body, headers = headers)
    data = response.json()
    order_id = json_normalize(data["orders"]).id.values[0]
    return(order_id)
        
def marketBuy(tgCurrency, qty, key, secret):
    
    secret_bytes = bytes(secret, encoding='utf-8')


    # Generating a timestamp.
    timeStamp = int(round(time.time() * 1000))

    body = {
      "side": "buy",    
      "order_type": "market_order", 
      "market": tgCurrency, #pair_market[pair] 
      "total_quantity": qty, #def qty
      "timestamp": timeStamp
    }

    json_body = json.dumps(body, separators = (',', ':'))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    url = "https://api.coindcx.com/exchange/v1/orders/create"

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': key,
        'X-AUTH-SIGNATURE': signature
    }

    response = requests.post(url, data = json_body, headers = headers)
    data = response.json()
    order_id = json_normalize(data["orders"]).id.values[0]
    return(order_id)
    
    
def qty(principal, close, tgCurrency):
    if tgCurrency in list(['B-MANA_BTC','B-SAND_BTC']):
        return round(principal/close, 0)
    else:
        return round(principal/close, 1)
    
def isOrderDone(order_id, key, secret):
    secret_bytes = bytes(secret, encoding='utf-8')

    # Generating a timestamp.
    timeStamp = int(round(time.time() * 1000))

    body = {
      "id": order_id, # Enter your Order ID here.
      "timestamp": timeStamp
    }

    json_body = json.dumps(body, separators = (',', ':'))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    url = "https://api.coindcx.com/exchange/v1/orders/status"

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': key,
        'X-AUTH-SIGNATURE': signature
    }

    response = requests.post(url, data = json_body, headers = headers)
    data = response.json()
    return data['status'] == "filled"

def is_consolidating(tgCurrency, percentage=2):
    
    url = "https://public.coindcx.com/market_data/candles?pair=" + tgCurrency + "&interval=1m"
    response = requests.get(url)
    try:
        data = response.json()
        candle = json_normalize(data)
        candle["time"]= pd.to_datetime(candle["time"],unit='ms').\
                                                       dt.tz_localize('utc').\
                                                       dt.tz_convert('Asia/Kolkata')
        #print("started")
        np_closes = candle.sort_values(by=['time'], ascending=True).close.values
        recent_candlesticks = np_closes[-15:]

        max_close = recent_candlesticks.max()
        min_close = recent_candlesticks.min()

        threshold = 1 - (percentage / 100)
        if min_close > (max_close * threshold):
            return True        

        return False
    except:
        return is_consolidating(tgCurrency = tgCurrency, percentage = percentage)
        
    

def is_breaking_out(tgCurrency, percentage=2.5):
    url = "https://public.coindcx.com/market_data/candles?pair=" + tgCurrency + "&interval=1m"
    response = requests.get(url)
    
    try:
        data = response.json()
        candle = json_normalize(data)
        candle["time"]= pd.to_datetime(candle["time"],unit='ms').\
                                                       dt.tz_localize('utc').\
                                                       dt.tz_convert('Asia/Kolkata')
        np_closes = candle.sort_values(by=['time'], ascending=True).close.values
        last_close = np_closes[-1]

        if is_consolidating(tgCurrency=tgCurrency, percentage=percentage):
            recent_closes = np_closes[-16:-1]

            if last_close > recent_closes.max():
                return True

        return False
    except:
        return is_breaking_out(tgCurrency = tgCurrency, percentage = percentage)


while(True):
    for pair in pairs:
        order_succeeded = True
        RSI_1M, close = rsi1m(pair, RSI_PERIOD)
        trend, RSI_4H, second_last_rsi = rsi4h(pair, RSI_PERIOD)
        last_closed_at[pair] = close
        if trend > 2:
            line = "going down"
        if trend <= 1:
            if second_last_rsi < RSI_4H:
                line = "going up"
        print (pair + ": " + str(RSI_1M) + ". Price: " + str(close))
        if pair in in_portfolio:
            investment[pair] = bought_at[pair]*bought_qty[pair]
            current[pair] = last_closed_at[pair]*bought_qty[pair]
            prof[pair] = round((current[pair] - investment[pair])*100/investment[pair],2)
            print(prof)
        if len(in_portfolio) == 0:
            prof = dict()
            investment = dict()
            current = dict()
            print("no position to show")
        if pair in in_portfolio:
            if RSI_1M > RSI_OVERBOUGHT:
                print("sell condition met")
                if prof[pair] > 3.5:
                    print("printing money")
                    #order_id = marketSell(pair_market[pair], qty, key, secret)
                    #while order_succeeded == False:
                    #    order_succeeded = isOrderDone(order_id, key, secret)
                    if order_succeeded:
                        in_portfolio.remove(pair)
                        #sold_at[pair] = data['avg_price']
                        pnl.append("Profit")
                        pnlr.append(prof[pair])
                else:
                    print("not making atleast 3.5%")
            if prof[pair] < -1.5:
                print("Stopping loss")
                #order_id = marketSell(pair_market[pair], qty, key, secret)
                #real: while order_succeeded == False:
                #real:    order_succeeded = isOrderDone(order_id, key, secret)
                if order_succeeded:
                    in_portfolio.remove(pair)
                    bought_at[pair] = close
                    pnl.append("Loss")
                    pnlr.append(prof[pair])
        if RSI_1M < RSI_OVERSOLD:
            if RSI_4H < 60:
                if line == "going up":
                    if pair not in in_portfolio:
                        print("buying")
                        print(trend)
                        quantity = qty(0.002, close, pair)
                        #real: order_id = marketBuy(pair_market[pair], quantity, key, secret)
                        #real: while order_succeeded == False:
                        #real:    order_succeeded = isOrderDone(order_id, key, secret)
                        if order_succeeded:
                            in_portfolio.append(pair)
                            bought_at[pair] = close#real: data['avg_price']
                            bought_qty[pair] = quantity
                    else:
                        print("already own")
                if RSI_4H < 30:
                    if pair not in in_portfolio:
                        print("buying")
                        quantity = qty(0.002, close, pair)
                        #real: order_id = marketBuy(pair_market[pair], quantity, key, secret)
                        #real: while order_succeeded == False:
                        #real:    order_succeeded = isOrderDone(order_id, key, secret)
                        if order_succeeded:
                            in_portfolio.append(pair)
                            bought_at[pair] = close#real: data['avg_price']
                            bought_qty[pair] = quantity
                    else:
                        print("already own")
            else: 
                print("market might go down, so not buying")
            
            #Simulation
            
        sleep(5)