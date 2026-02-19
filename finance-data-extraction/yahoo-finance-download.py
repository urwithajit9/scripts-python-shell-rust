import yfinance as yf

data = yf.download(
    "NVDA SMCI VFS ADANIPOWER.NS TATAMOTORS.NS 035720.KS  035420.KS VEDL.NS",
    start="2024-11-01",
    end="2024-12-04",
)
# print(data)
# print(data["NVDA"])
# print(data["SMCI"])

# data = yf.download("SPY AAPL", start="2017-01-01", end="2024-12-05", group_by="ticker")

# print(data["Volume"]["ADANIPOWER.NS"])
print(data)
