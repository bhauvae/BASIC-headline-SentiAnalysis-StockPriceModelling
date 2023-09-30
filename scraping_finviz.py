# %%
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from tickers import stocks as tickers
import pandas as pd

finviz_url = "https://finviz.com/quote.ashx?t="
# %%
news_data = pd.Series(index=tickers)
for ticker in tickers:
    df = pd.DataFrame()
    url = finviz_url + ticker
    req = Request(url=url, headers={"user-agent": "my-app"})
    response = urlopen(req)
    soup = BeautifulSoup(response, "lxml")
    news_table = soup.find(id="news-table")
    news_table_rows = news_table.find_all("tr")
    data = []
    for index, row in enumerate(news_table_rows):
        headline = row.a.text
        timestamp = row.td.text.strip().split(" ")
        if len(timestamp) != 1:
            date = timestamp[0]
            time = timestamp[1]
        else:
            time = timestamp[0]

        link = row.a["href"]

        data.append([date, time, headline, link])

    df = pd.DataFrame(data, columns=["Date", "Time", "Headlines", "Links"])
    news_data[ticker] = df


# %%
