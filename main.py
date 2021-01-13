import pandas as pd
import numpy as np
import yfinance as yf
import bs4 as bs
import requests
import datetime


resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
soup = bs.BeautifulSoup(resp.text, 'lxml')
table = soup.find('table', {'class': 'wikitable sortable'})
tickers = []
for row in table.findAll('tr')[1:]:
    ticker = row.findAll('td')[0].text
    tickers.append(ticker)

tickers = [s.replace('\n', '') for s in tickers]
# we will define two horizon, a long trading horizon and a short trading horizon

startlong = datetime.datetime(2015,10,1)
endlong = datetime.datetime(2019,12,31)

startshort = datetime.datetime(2018,12,10)
endshort = endlong

interval = "1d"

datalong = yf.download(tickers, start=startlong, end=endlong,interval=interval)
df1 = datalong['Close']

datashort = yf.download(tickers, start=startshort, end=endshort,interval=interval)
df2 = datashort['Close']

#reproduce our data so we won't have to download them anymore
df = df1
dfs = df2

#delete col with na only
for col in df.columns:
  if df[col].isnull().sum()==df.shape[0]:
    df = df.drop(col,axis=1)

#same for datashort
for col in dfs.columns:
  if dfs[col].isnull().sum()==dfs.shape[0]:
    dfs = dfs.drop(col,axis=1)

#treat our nas
for col in df.columns:
  df[col] = df[col].fillna(np.mean(df[col]))

#same for datashort
for col in dfs.columns:
  dfs[col] = dfs[col].fillna(np.mean(df[col]))

#set the desire level of sensibility
level = .8

#correlation matrix
corlong = df.corr()
corshort=dfs.corr()

#check if my correlation differ
to_trade =list()

for row in range(corlong.shape[0]): 
  for col in range(corlong.shape[0]):
    min = corlong.iloc[row,col]-level
    max = corlong.iloc[row,col]+level
    if corshort.iloc[row,col] <= min or corshort.iloc[row,col] >= max:
      stock=corshort.index[row]+" vs "+corshort.columns[col]
      to_trade.append(stock)


print(len(np.unique(to_trade)))
print(to_trade)