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

url = "https://api.coindcx.com/exchange/v1/markets"

response = requests.get(url)
data = response.json()
#print(data)

url = "https://api.coindcx.com/exchange/v1/markets_details"

response = requests.get(url)
data = response.json()

df = json_normalize(data)

#print(df)

#coins = dict()
#df = df.loc[df['base_currency_short_name'].isin(["BTC"])]


market_pair = dict()
'''for i in df.index:
    for order in df.order_types[i]:
        if order == 'market_order':
            coins[df.pair[i]] = df.coindcx_name[i]'''

#pairs = list(coins.keys())
#pair_market = coins

df = df.loc[df['coindcx_name'].isin(["AXSBTC", "MANABTC", "ENJBTC", "SANDBTC", "ERNBTC", "YGGBTC", "ALICEBTC", "ILVBTC", "BNBBTC", "FTTBTC", "CAKEBTC", "UNIBTC", "LRCBTC", "MATICBTC", "AAVEBTC", "MKRBTC", "RUNEBTC", "CRVBTC", "COMPBTC", "DYDXBTC", "SUSHIBTC", "YFIBTC", "ZRXBTC", "XRPBTC", "DOTBTC", "ALGOBTC", "LUNABTC", "LINKBTC", "AVAXBTC", "LTCBTC", "SOLBTC", "ETHBTC", "ADABTC"])]
pairs = df.pair.values
markets = df.coindcx_name.values
for i in range(len(pairs)):
    market_pair[pairs[i]] = markets[i]
print(market_pair)

#pair_market = {'B-ENJ_BTC': 'ENJBTC', 'B-ILV_BTC': 'ILVBTC', 'B-ALICE_BTC':'ALICEBTC', 'B-SAND_BTC':'SANDBTC', 'B-YGG_BTC':'YGGBTC',
# 'B-MANA_BTC':'MANABTC', 'B-AXS_BTC':'AXSBTC'}

key = "***"
secret = "***"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

'''
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
        return rsi1d(tgCurrency = tgCurrency, RSI_PERIOD = RSI_PERIOD)
    
'''
    
def rsi4h(tgCurrency, RSI_PERIOD):
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
        return rsi4h(tgCurrency = tgCurrency, RSI_PERIOD = RSI_PERIOD)


last_5_rsi, last_rsi, second_last_rsi, price= rsi4h('B-SCRT_BTC', 14)

import matplotlib.pyplot as plt
plt.figure(figsize=(12.2, 4.5))
plt.plot(price['Price'], label='Price')
plt.title('Close Price History')
plt.xlabel('Date')
plt.ylabel('close')
plt.show()

ShortEMA=price.Price.ewm(span=12, adjust = False).mean()
LongEMA=price.Price.ewm(span=26, adjust = False).mean()
MACD = ShortEMA - LongEMA
Signal = MACD.ewm(span=9, adjust = False).mean()

plt.figure(figsize=(12.2, 4.5))
plt.plot(price.index, MACD, label = 'SCRT_BTC MACD', color = 'red')
plt.plot(price.index, Signal, label = 'SCRT_BTC Signal', color = 'blue')
plt.legend(loc = 'upper left')
plt.show()

price['MACD'] = MACD
price['Signal'] = Signal

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

a = buy_sell(price)
price['Buy_Signal_Price'] = a[0]
price['Sell_Signal_Price'] = a[1]
price['Diff'] = price["MACD"] - price["Signal"]
#price
#with pd.option_context('display.max_rows', None,
#                       'display.max_columns', None,
#                       'display.precision', 3,
#                       ):
    #print(price)

plt.figure(figsize=(12.2, 4.5))
plt.scatter(price.index, price['Buy_Signal_Price'], label = 'Buy', color = 'green', marker = '^', alpha = 1)

plt.scatter(price.index, price['Sell_Signal_Price'], label = 'Sell', color = 'red', marker = 'v', alpha = 1)
plt.plot(price['Price'], label='Price')
plt.title('Close Price History')
plt.xlabel('Date')
plt.ylabel('close')
plt.show()
plt.figure(figsize=(12.2, 4.5))
plt.plot(price.index, price.RSI, label = 'RSI', color = 'blue')
plt.ylabel('RSI')
plt.show()
plt.figure(figsize=(12.2, 4.5))
plt.plot(price.index, MACD, label = 'SCRT_BTC MACD', color = 'red')
plt.plot(price.index, Signal, label = 'SCRT_BTC Signal', color = 'blue')
plt.legend(loc = 'upper left')
plt.show()


fig,ax=plt.subplots(figsize=(12.2, 4.5))
ax.scatter(price.index, price['Buy_Signal_Price'], label = 'Buy', color = 'green', marker = '^', alpha = 1)
ax.scatter(price.index, price['Sell_Signal_Price'], label = 'Sell', color = 'red', marker = 'v', alpha = 1)
ax.plot(price['Price'], label='Price')
#ax.title('Close Price History')
#ax.xlabel('Date')
#ax.ylabel('close')
#ax.show()
# set x-axis label
ax.set_xlabel("Date",fontsize=14)
# set y-axis label
ax.set_ylabel("Price",color="red",fontsize=14)
# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(price.index, price.RSI, label = 'RSI', color = 'blue')
#ax2.plot(gapminder_us.year, gapminder_us["gdpPercap"],color="blue",marker="o")
ax2.set_ylabel("RSI",color="blue",fontsize=14)
ax.grid()
plt.grid()
plt.show()

# save the plot as a file
#fig.savefig('two_different_y_axis_for_single_python_plot_with_twinx.jpg',
#            format='jpeg',
#            dpi=100,
#            bbox_inches='tight')
#plt.show()