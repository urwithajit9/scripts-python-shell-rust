import yfinance as yf

msft = yf.Ticker("MSFT")
print(msft)

# get stock info
print(msft.info)

# get historical market data
print(msft.history(period="1d", interval="15m"))
"""
period: data period to download (Either Use period parameter or use start and end) Valid periods are: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
interval: data interval (intraday data cannot extend last 60 days) Valid intervals are: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
start: If not using period - Download start date string (YYYY-MM-DD) or datetime.
end: If not using period - Download end date string (YYYY-MM-DD) or datetime.
prepost: Include Pre and Post market data in results? (Default is False)
auto_adjust: Adjust all OHLC automatically? (Default is True)
actions: Download stock dividends and stock splits events? (Default is True)

"""

# show actions (dividends, splits)
print(msft.actions)

# show dividends
print(msft.dividends)

# show splits
print(msft.splits)
