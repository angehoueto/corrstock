# corrstock
Generate trading signals through stock correlation deviation

This model is really incomplete. THe backtesting is still on work to compute the optimal value for deviation. When we will have that value we will be able to develop a trading strategy. Actually our model will just show us what stocks are deviating from their historical correlation. We will complete this model as soon as possible by adding a trading strategy to it.

## Libraries

We will first import the library that we will use in our model:
datetime, pandas and numpy for data modeling
yfinance to get our financial data
beautifulsoup to scrap web to automate stock tickers request

```{r}
import pandas as pd
import numpy as np
import yfinance as yf
import bs4 as bs
import requests
import datetime
```

## Download data

We will access to the html code of the link where our stock codes are located, then we will click on inspect element to find where our stocks names are stored, we will find it class type and then trough a loop we will download each of our tickers

```{r}
resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
soup = bs.BeautifulSoup(resp.text, 'lxml')
table = soup.find('table', {'class': 'wikitable sortable'})
tickers = []
for row in table.findAll('tr')[1:]:
    ticker = row.findAll('td')[0].text
    tickers.append(ticker)
tickers = [s.replace('\n', '') for s in tickers]
```

Let's now define the period where we will compute each correlation, we will have our long correlation perido and our short correlation period, be sure that you take periods that are not impacted with certain events as in March 2020 where the market was down because of the coronavirus pandemic.
```{r}
startlong = datetime.datetime(2015,10,1)
endlong = datetime.datetime(2019,12,31)

startshort = datetime.datetime(2018,12,10)
endshort = endlong

```
We will now download our data:
```{r}
interval = "1d"

datalong = yf.download(tickers, start=startlong, end=endlong,interval=interval)
df1 = datalong['Close']

datashort = yf.download(tickers, start=startshort, end=endshort,interval=interval)
df2 = datashort['Close']
```


We will clean our data before our model implementation.
```{r}
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

```

##Model
As we said it earlier this model is not complete, we are still backtesting our model to find the optimal level of deviation in our correlation to maximize our trading signals so for now the user should imput as deviation level what he think to be great, after our backtesting we will give the right value on this repository.
```{r}
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
```

