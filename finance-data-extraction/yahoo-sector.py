import yfinance as yf

# tech = yf.Sector("technology")
# software = yf.Industry("software-infrastructure")


# Common information
# tech.key
# tech.name
# tech.symbol
# print(tech.ticker)
# # tech.overview
# print(tech.top_companies)
# tech.research_reports

# # Sector information
# tech.top_etfs
# tech.top_mutual_funds
# tech.industries

# # Industry information
# software.sector_key
# software.sector_name
# software.top_performing_companies
# software.top_growth_companies

# ticker = "ADANIPOWER.NS" #NSE
ticker = "ADANIPOWER.BO"  # BSE
# Alpha Vantage, Quandl,


stock = yf.Ticker(ticker)

# Fetch sector and industry information
sector = stock.info.get("sector", "Sector not available")
industry = stock.info.get("industry", "Industry not available")

print(f"Sector: {sector}")
print(f"Industry: {industry}")

utilities = yf.Sector("utilities")
print(utilities.top_companies)
