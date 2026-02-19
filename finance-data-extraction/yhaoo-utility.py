import yfinance as yf

# Define a list of top utility companies (example tickers)
utility_tickers = ["NEE", "DUK", "SO", "EXC", "AEP"]  # Add more if needed

# Fetch data for each ticker
for ticker in utility_tickers:
    stock = yf.Ticker(ticker)
    print(f"Company: {stock.info.get('shortName', 'N/A')}")
    print("Sector:", stock.info.get("sector", "N/A"))
    print("Industry:", stock.info.get("industry", "N/A"))
    print("Market Cap:", stock.info.get("marketCap", "N/A"))
    print("-" * 40)
