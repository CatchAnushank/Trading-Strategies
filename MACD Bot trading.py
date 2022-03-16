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
import time
import math

url = "https://api.coindcx.com/exchange/v1/markets_details"

response = requests.get(url)
data = response.json()

df = json_normalize(data)

df = df.loc[df['coindcx_name'].isin(["KNCUSDT", "LINKUSDT", "AXSUSDT", "MANAUSDT", "BATUSDT","ENJUSDT", "SANDUSDT", "ERNUSDT", "YGGUSDT", "ALICEUSDT", "ILVUSDT", "BNBUSDT", "FTTUSDT", "CAKEUSDT", "LRCUSDT", "MATICUSDT", "AAVEUSDT", "RUNEUSDT", "CRVUSDT", "COMPUSDT", "DYDXUSDT", "SUSHIUSDT", "YFIUSDT", "ZRXUSDT", "XRPUSDT", "DOTUSDT", "ALGOUSDT", "LUNAUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT", "SOLUSDT", "ETHUSDT", "ADAUSDT", "XMRUSDT", "ZECUSDT", "FIROUSDT", "ATOMUSDT", "ONEUSDT", "FTMUSDT"])]

df = df.iloc[:,[0,5,12,-2]]

len(df)

def rsi4h(tgCurrency, RSI_PERIOD):
    i=0
    url = "https://public.coindcx.com/market_data/candles?pair=" + tgCurrency + "&interval=4h"
    response = requests.get(url)
    try:
        data = response.json()
        candle = json_normalize(data)
        candle["time"]= pd.to_datetime(candle["time"],unit='ms').\
                                                       dt.tz_localize('utc').\
                                                       dt.tz_convert('Asia/Kolkata')
        np_closes = candle.sort_values(by=['time'], ascending=True).close.values
        time = candle.sort_values(by=['time'], ascending=True).time.values
        df = pd.DataFrame({'Time': time, 'Price': np_closes})
        df = df.set_index(pd.DatetimeIndex(df['Time'].values))
        close = np_closes[-1]
        rsi = talib.RSI(np_closes, RSI_PERIOD)
        last_rsi = rsi[-1]
        return last_rsi, close, df, rsi
    except:
        i = i + 1
        if i <= 3:
            return rsi4h(tgCurrency = tgCurrency, RSI_PERIOD = RSI_PERIOD)
        else:
            pass

        
        
def rsi1m(tgCurrency, RSI_PERIOD):
    i=0
    url = "https://public.coindcx.com/market_data/candles?pair=" + tgCurrency + "&interval=1m"
    response = requests.get(url)
    try:
        data = response.json()
        candle = json_normalize(data)
        candle["time"]= pd.to_datetime(candle["time"],unit='ms').\
                                                       dt.tz_localize('utc').\
                                                       dt.tz_convert('Asia/Kolkata')
        np_closes = candle.sort_values(by=['time'], ascending=True).close.values
        time = candle.sort_values(by=['time'], ascending=True).time.values
        df = pd.DataFrame({'Time': time, 'Price': np_closes})
        df = df.set_index(pd.DatetimeIndex(df['Time'].values))
        close = np_closes[-1]
        rsi = talib.RSI(np_closes, RSI_PERIOD)
        last_rsi = rsi[-1]
        return last_rsi, close, df, np_closes
    except:
        i = i + 1
        if i <= 3:
            return rsi1m(tgCurrency = tgCurrency, RSI_PERIOD = RSI_PERIOD)
        else:
            pass
        

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
    
    
def qty(principal, close, tgCurrency, precision):
        return round(principal/close, precision)
    
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

def buy_sell(signal):
    Buy = []
    Sell = []
    flag = -1
    
    for i in range(0, len(signal)):
        if signal['MACD'][i] > signal['Signal'][i]:
            Sell.append(np.nan)
            if flag != 1:
                Buy.append(signal['Price'][i])
                flag = 1
            else:
                Buy.append(np.nan)
        elif signal['MACD'][i] < signal['Signal'][i]:
            Buy.append(np.nan)
            if flag != 0:
                Sell.append(signal['Price'][i])
                flag = 0
            else:
                Sell.append(np.nan)
        else:
            Buy.append(np.nan)
            Sell.append(np.nan)
    return (Buy, Sell)

portfolio = list()
pnl = list()

#portfolio_table = pd.DataFrame(portfolio, columns=['pair', 'qyt', 'entry_price', 'timestamp', 'current_price', 'profit'])
pnl_table = pd.DataFrame(pnl, columns=['pair', 'qyt', 'entry_price', 'timestamp', 'exit_price', 'profit', 'exit_time'])


#pnl_table = pd.read_csv('pnl_MACD.csv', encoding='utf-8', index=False)
portfolio_table = pd.read_csv('portfolio_MACD.csv')

#for i in range(len(pnl_table)):
#    pnl.append(list(pnl_table.iloc[i,:]))

for i in range(len(portfolio_table)):
    portfolio.append(list(portfolio_table.iloc[i,:]))

while True:
    j = 1
    for pair in df.pair.values:
        #print(pair)
        try:
            last_rsi, close, price, RSI= rsi4h(pair, 14)
            last_rsi_1m, close1m, price_1m, RSI_1m = rsi1m(pair, 14)
        except:
            next
        ShortEMA=price.Price.ewm(span=12, adjust = False).mean()
        LongEMA=price.Price.ewm(span=26, adjust = False).mean()
        MACD = ShortEMA - LongEMA
        Signal = MACD.ewm(span=9, adjust = False).mean()
        price['MACD'] = MACD
        price['Signal'] = Signal
        a = buy_sell(price)
        price['Buy_Signal_Price'] = a[0]
        price['Sell_Signal_Price'] = a[1]
        price['Diff'] = price["Signal"] - price["MACD"]
        price['RSI'] = RSI
        #print(price)
        #print(j, "----------------------------------------", pair)
        
        #Buying signal monitoring
        
        if pair not in portfolio_table.loc[:,"pair"].values:
            if not(math.isnan(price.iloc[-1,4])):

                print("Just Crossed lines - BUY - 4h ", pair )
                if price.iloc[-1,-1] < 80:
                    precision = df.iloc[np.where(df["pair"] == pair)[0][0], 2]
                    qty = round(20/close1m, precision)
                    #order_id = marketBuy(pair, qty, key, secret)
                    portfolio.append([pair, qty, close1m, int(round(time.time() * 1000)), close1m, 0])
                    portfolio_table = pd.DataFrame(portfolio, columns=['pair', 'qty', 'entry_price', 'timestamp', 'current_price', 'profit'])
                    portfolio_table.to_csv('portfolio_MACD.csv', encoding='utf-8', index=False)

            if price.iloc[-3,5] > price.iloc[-2,5] and price.iloc[-1, 5] > price.iloc[-2,5]:

                print("About to cross lines - BUY - 4h ", pair )
                if price.iloc[-1,-1] < 80:
                    precision = df.iloc[np.where(df["pair"] == pair)[0][0], 2]
                    qty = round(20/close1m, precision)
                    #order_id = marketBuy(pair, qty, key, secret)
                    portfolio.append([pair, qty, close1m, int(round(time.time() * 1000)), close1m, 0])
                    portfolio_table = pd.DataFrame(portfolio, columns=['pair', 'qty', 'entry_price', 'timestamp', 'current_price', 'profit'])
                    portfolio_table.to_csv('portfolio_MACD.csv', encoding='utf-8', index=False)
        
        #Portfolio monitoring
        
        if pair in portfolio_table.loc[:,"pair"].values:
            #print("TRUE")
            portfolio_table.iloc[(np.where(portfolio_table["pair"] == pair)[0][0]), -2] = close1m
            portfolio_table.iloc[(np.where(portfolio_table["pair"] == pair)[0][0]), -1] = (close1m - portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0], 2])*100/portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0], 2]
        
        #sell signal monitoring
        
        if pair in portfolio_table.loc[:,"pair"].values:
            if not(math.isnan(price.iloc[-3,5])) or not(math.isnan(price.iloc[-2,5])) or not(math.isnan(price.iloc[-1,5])):
                #order_id = marketBuy(pair, qty, key, secret)
                
                pnl.append([portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],0], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],1], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],2], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],3], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],4], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],5], int(round(time.time() * 1000))])
                portfolio.remove(portfolio[np.where(portfolio_table["pair"] == pair)[0][0]])
                portfolio_table = pd.DataFrame(portfolio, columns=['pair', 'qty', 'entry_price', 'timestamp', 'current_price', 'profit'])
                pnl_table = pd.DataFrame(pnl, columns=['pair', 'qyt', 'entry_price', 'timestamp', 'exit_price', 'profit', 'exit_time'])
                pnl_table.to_csv('pnl_MACD.csv', encoding='utf-8', index=False)
                print("Just Crossed lines - SELL - 4h ", pair )

            elif price.iloc[-3,5] < price.iloc[-2,5] and price.iloc[-1, 5] < price.iloc[-2,5]:

                pnl.append([portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],0], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],1], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],2], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],3], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],4], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],5], int(round(time.time() * 1000))])
                portfolio.remove(portfolio[np.where(portfolio_table["pair"] == pair)[0][0]])
                portfolio_table = pd.DataFrame(portfolio, columns=['pair', 'qty', 'entry_price', 'timestamp', 'current_price', 'profit'])
                pnl_table = pd.DataFrame(pnl, columns=['pair', 'qyt', 'entry_price', 'timestamp', 'exit_price', 'profit', 'exit_time'])
                pnl_table.to_csv('pnl_MACD.csv', encoding='utf-8', index=False)
                print("About to Cross lines - SELL - 4h ", pair )
            
            elif price.iloc[-1,-1] > 80:
                
                pnl.append([portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],0], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],1], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],2], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],3], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],4], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],5], int(round(time.time() * 1000))])
                portfolio.remove(portfolio[np.where(portfolio_table["pair"] == pair)[0][0]])
                portfolio_table = pd.DataFrame(portfolio, columns=['pair', 'qty', 'entry_price', 'timestamp', 'current_price', 'profit'])
                pnl_table = pd.DataFrame(pnl, columns=['pair', 'qyt', 'entry_price', 'timestamp', 'exit_price', 'profit', 'exit_time'])
                pnl_table.to_csv('pnl_MACD.csv', encoding='utf-8', index=False)
                print("OVERBOUGHT - SELL - 4h ", pair )
            
            elif portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0], -1] <= -4:
                
                pnl.append([portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],0], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],1], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],2], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],3], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],4], portfolio_table.iloc[np.where(portfolio_table["pair"] == pair)[0][0],5], int(round(time.time() * 1000))])
                portfolio.remove(portfolio[np.where(portfolio_table["pair"] == pair)[0][0]])
                portfolio_table = pd.DataFrame(portfolio, columns=['pair', 'qty', 'entry_price', 'timestamp', 'current_price', 'profit'])
                pnl_table = pd.DataFrame(pnl, columns=['pair', 'qyt', 'entry_price', 'timestamp', 'exit_price', 'profit', 'exit_time'])
                pnl_table.to_csv('pnl_MACD.csv', encoding='utf-8', index=False)
                print("StopLoss or StopProfit - SELL - 4h ", pair )
                #print(pnl_table)
                             
        #if perc_return > 10:
         #   print(df.iloc[j, 1], ": ", perc_return)
        #if perc_return < -4:
        #    print(df.iloc[j, 1], ": ", perc_return)


        j = j + 1
    
    print(portfolio_table)
    print(pnl_table)