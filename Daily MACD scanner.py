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

url = "https://api.coindcx.com/exchange/v1/markets"

response = requests.get(url)
data = response.json()
#print(data)

url = "https://api.coindcx.com/exchange/v1/markets_details"

response = requests.get(url)
data = response.json()

df = json_normalize(data)

coins = dict()
df = df.loc[df['base_currency_short_name'].isin(["USDT"])]


market_pair = dict()
for i in df.index:
    for order in df.order_types[i]:
        if order == 'limit_order':
            coins[df.pair[i]] = df.coindcx_name[i]

print(coins)
pairs = list(coins.keys())
pair_market = coins

key = "****"
secret = "****"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

in_portfolio = list()
pnl = list()
pnlr = list()
last_closed_at = dict()
prof = dict()
investment = dict()
current = dict()

def rsi1d(tgCurrency, RSI_PERIOD):
    i=0
    url = "https://public.coindcx.com/market_data/candles?pair=" + tgCurrency + "&interval=1d"
    response = requests.get(url)
    try:
        data = response.json()
        candle = json_normalize(data)
        candle["time"]= pd.to_datetime(candle["time"],unit='ms').\
                                                       dt.tz_localize('utc').\
                                                       dt.tz_convert('Asia/Kolkata')
        #print("started")
        np_closes = candle.sort_values(by=['time'], ascending=True).close.values
        #print("working1")
        time = candle.sort_values(by=['time'], ascending=True).time.values
        #print("working2")
        df = pd.DataFrame({'Time': time, 'Price': np_closes})
        df = df.set_index(pd.DatetimeIndex(df['Time'].values))
        #print("working3")
        #print(df)
        close = np_closes[-1]
        rsi = talib.RSI(np_closes, RSI_PERIOD)
            #print("all rsis calculated so far")
            #print(rsi)
        last_rsi = rsi[-1]
            #print(candle[["close", "time"]].iloc[[0]])
        #print("the current rsi for " + pair + " is {}".format(last_rsi))
        return last_rsi, close, df
    except:
        i = i + 1
        if i <= 3:
            return rsi1d(tgCurrency = tgCurrency, RSI_PERIOD = RSI_PERIOD)
        else:
            pass
    

    
def rsi4h(tgCurrency, RSI_PERIOD, i=0):
    url = "https://public.coindcx.com/market_data/candles?pair=" + tgCurrency + "&interval=4h"
    response = requests.get(url)
    try:
        data = response.json()
        candle = json_normalize(data)
        candle["time"]= pd.to_datetime(candle["time"],unit='ms').\
                                                       dt.tz_localize('utc').\
                                                       dt.tz_convert('Asia/Kolkata')
        #print("started")
        np_closes = candle.sort_values(by=['time'], ascending=True).close.values
        time = candle.sort_values(by=['time'], ascending=True).time.values
        #print("working2")
        df = pd.DataFrame({'Time': time, 'Price': np_closes})
        df = df.set_index(pd.DatetimeIndex(df['Time'].values))
        close = np_closes[-1]
        rsi = talib.RSI(np_closes, RSI_PERIOD)
        df['RSI'] = rsi
        #print("rsi 2h for: " + str (tgCurrency))
        #print(rsi)
        last_rsi = rsi[-1]
        second_last_rsi = rsi[-2]
            #print(candle[["close", "time"]].iloc[[0]])
            #print("the current rsi for " + pair + " is {}".format(last_rsi))
        trend = rsi > last_rsi
        #print(rsi[494:500])
        #print((trend == True)[494:499])
        #print(np.where(trend == True)[-1])
        return sum((trend == True)[494:498]), last_rsi, second_last_rsi, df
    except:
        i = i + 1
        if i <= 3:
            return rsi4h(tgCurrency = tgCurrency, RSI_PERIOD = RSI_PERIOD, i=i)
        else:
            pass

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
#price
#with pd.option_context('display.max_rows', None,
#                       'display.max_columns', None,
#                       'display.precision', 3,
#                       ):
    #print(price)
j = 1
for pair in pairs:
    #print(pair)
    try:
        last_5_rsi, last_rsi, second_last_rsi, price= rsi4h(pair, 14)
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
    print("----------------------------------------", pair)
    if not(math.isnan(price.iloc[-3,5])) or not(math.isnan(price.iloc[-2,5])) or not(math.isnan(price.iloc[-1,5])):
        print("Just Crossed lines - 4h  ", pair )

    if price.iloc[-3,7] > price.iloc[-2,7] and price.iloc[-1, 7] > price.iloc[-2,7]:
        print("buy: ", pair, "for a 4h")
        with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
            print(price.iloc[[-3,-2,-1],:])
        #print(price.iloc[[-3,-2,-1],:])

    #if price.iloc[-3,7] < price.iloc[-2,7] and price.iloc[-1, 7] < price.iloc[-2,7]:
        #print("sell: ", pair, "for a 4h")
        #print(price.iloc[[-3,-2,-1],:])
    #print(price)
    rsi, close, price= rsi1d('B-RGT_USDT', 14)
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
    #print(price)
    print("----------------------------------------")
    
    if price.iloc[-3,6] > price.iloc[-2,6] and price.iloc[-1, 6] > price.iloc[-2,6]:
        print("Buy ", pair, "for a 1d")
        #print(price.iloc[[-3,-2,-1],:])
    
    if not(math.isnan(price.iloc[-3,4])) or not(math.isnan(price.iloc[-2,4])) or not(math.isnan(price.iloc[-1,4])):
        print("Just Crossed lines - 1d  ", pair )

    #if price.iloc[-3,6] < price.iloc[-2,6] and price.iloc[-1, 6] < price.iloc[-2,6]:
        #print("sell ", pair, "for a 1d")
        #print(price.iloc[[-3,-2,-1],:])
        
    j = j+1
    print(str(j)+"/"+str(len(pairs)))