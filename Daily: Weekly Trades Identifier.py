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
print(data)

url = "https://api.coindcx.com/exchange/v1/markets_details"

response = requests.get(url)
data = response.json()

df = json_normalize(data)

#print(df)

coins = dict()
df = df.loc[df['base_currency_short_name'].isin(["INR"])]


market_pair = dict()
for i in df.index:
    for order in df.order_types[i]:
        if order == 'limit_order':
            coins[df.pair[i]] = df.coindcx_name[i]

print(coins)
pairs = list(coins.keys())
pair_market = coins

'''df = df.loc[df['coindcx_name'].isin(["AXSBTC", "MANABTC", "ENJBTC", "SANDBTC", "ERNBTC", "YGGBTC", "ALICEBTC", "ILVBTC", "BNBBTC", "FTTBTC", "CAKEBTC", "UNIBTC", "LRCBTC", "MATICBTC", "AAVEBTC", "MKRBTC", "RUNEBTC", "CRVBTC", "COMPBTC", "DYDXBTC", "SUSHIBTC", "YFIBTC", "ZRXBTC", "XRPBTC", "DOTBTC", "ALGOBTC", "LUNABTC", "LINKBTC", "AVAXBTC", "LTCBTC", "SOLBTC", "ETHBTC", "ADABTC"])]
pairs = df.pair.values
markets = df.coindcx_name.values
for i in range(len(pairs)):
    market_pair[pairs[i]] = markets[i]
print(market_pair)'''

def rsi1d(tgCurrency, RSI_PERIOD):
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
        close = np_closes[-1]
        rsi = talib.RSI(np_closes, RSI_PERIOD)
            #print("all rsis calculated so far")
            #print(rsi)
        last_rsi = rsi[-1]
        second_last_rsi = rsi[-2]
            #print(candle[["close", "time"]].iloc[[0]])
            #print("the current rsi for " + pair + " is {}".format(last_rsi))
        trend = rsi > last_rsi
        #print(rsi[494:500])
        #print((trend == True)[494:499])
        #print(np.where(trend == True)[-1])
        return sum((trend == True)[494:498]), last_rsi, second_last_rsi
    except:
        return rsi1d(tgCurrency = tgCurrency, RSI_PERIOD = RSI_PERIOD)
    
def rsi1w(tgCurrency, RSI_PERIOD):
    url = "https://public.coindcx.com/market_data/candles?pair=" + tgCurrency + "&interval=1w"
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
        #print(rsi[494:500])
        #print((trend == True)[494:499])
        #print(np.where(trend == True)[-1])
        return sum((trend == True)[494:498]), last_rsi, second_last_rsi
    except:
        return rsi1d(tgCurrency = tgCurrency, RSI_PERIOD = RSI_PERIOD)

for pair in pairs:
    try:
        RSI_1D, last, second_last = rsi1d(pair, 14)
        RSI_1W, lastW, second_lastW = rsi1w(pair, 14)
        print('-----' + pair + '----')
        if last < 30:
            print(pair, last, " - 1 Day")
        if lastW < 30:
            print(pair, lastW, " - 1 week")
    except:
        print('Error in ' + str(pair))
        next
    