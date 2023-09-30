# %%
import yfinance as yf
from tickers import stocks as tickers
import pandas as pd

# %%
technical_data = {}
for ticker in tickers:
    technical_data[ticker] = yf.Ticker(ticker)
    technical_data[ticker] = technical_data[ticker].history(period="max")[["Close"]]
    technical_data[ticker].index = pd.to_datetime(technical_data[ticker].index).date

    technical_data[ticker]["Next Day"] = technical_data[ticker]["Close"].shift(-1)

    technical_data[ticker]["Target"] = -(
        (-1) ** (technical_data[ticker]["Next Day"] >= technical_data[ticker]["Close"])
    )

# %%
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=200, min_samples_split=50, random_state=1)


# %%
def predict(train, test, model, predictors):
    model.fit(train[predictors], train["Target"])
    pred = model.predict(test[predictors])
    pred = pd.Series(pred, index=test.index, name="Predictions")
    combined = pd.concat([test["Target"], pred], axis=1)
    return combined


# %%
def backtest(data, model, predictors, start=1250, step=125):
    all_predictions = []
    for i in range(start, data.shape[0], step):
        train = data.iloc[0:i].copy()
        test = data.iloc[i : (i + step)].copy()
        predictions = predict(train, test, model, predictors)
        all_predictions.append(predictions)

    return pd.concat(all_predictions)


# %%
horizons = [2, 5, 60, 250, 1000]
predictors = []
for horizon in horizons:
    ratio_column = f"Close_Ratio_{horizon}"
    trend_column = f"Trend_{horizon}"
    predictors += [ratio_column, trend_column]


def indicators(data):
    for horizon in horizons:
        rolling_avg = data.rolling(horizon).mean()

        ratio_column = f"Close_Ratio_{horizon}"
        data[ratio_column] = data["Close"] / rolling_avg["Close"]

        trend_column = f"Trend_{horizon}"
        data[trend_column] = data.shift(1).rolling(horizon).sum()["Target"]


# %%

for ticker in tickers:
    indicators(technical_data[ticker])
    technical_data[ticker] = technical_data[ticker].dropna()


# %%
from sklearn.metrics import precision_score

score_list = []
for ticker in tickers:
    predictions = backtest(technical_data[ticker], model, predictors)
    score_list.append(precision_score(predictions["Target"], predictions["Predictions"]))

score = pd.DataFrame({"Tickers":tickers,"Score":score_list})
# %%
