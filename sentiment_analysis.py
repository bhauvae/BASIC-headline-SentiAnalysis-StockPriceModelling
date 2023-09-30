# %%
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from scraping_finviz import news_data
from tickers import stocks as tickers
# %%
vader = SentimentIntensityAnalyzer()
# %%
sentiment_data = pd.Series(index=tickers)

for ticker in tickers:
    news_data[ticker]["Compound"] = news_data[ticker]["Headlines"].apply(
        lambda headline: vader.polarity_scores(headline)["compound"]
    )

    news_data[ticker]["Date"] = pd.to_datetime(news_data[ticker].Date).dt.date
    news_data[ticker]["Time"] = pd.to_datetime(news_data[ticker].Time).dt.time

    data = news_data["AMZN"].groupby("Date")["Compound"].mean()
    sentiment_data[ticker] = pd.DataFrame({"Score": data.values}, index=data.index)


# %%
