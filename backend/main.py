from agmarknet_loader import get_markets_by_district
from fastapi import FastAPI
from agmarknet import get_prices, get_summary, get_commodities, get_districts, get_markets

app = FastAPI()


# Root health-check endpoint
@app.get("/")
def home():
    """Simple health-check returning running status."""
    return {"message": "AgriPrice Backend Running"}


# Returns price records for a commodity
@app.get("/prices")
def prices(commodity: str, district: str = None, market: str = None):
    """API endpoint returning price records for a commodity.

    Args:
        commodity: Commodity name to query.
        district: Optional district name to filter.
        market: Optional market name to filter.

    Returns:
        JSON-serializable list of price records or message dict.
    """
    return get_prices(commodity, district, market)


# Returns aggregated summary statistics for a commodity
@app.get("/summary")
def summary(commodity:str, district:str = None, market:str = None):
    """API endpoint returning modal price summary for a commodity.

    Args:
        commodity: Commodity name to summarize.
        district: Optional district to restrict summary.
        market: Optional market to restrict summary.

    Returns:
        JSON-serializable dictionary with summary statistics.
    """
    return get_summary(commodity, district, market)


# Returns available commodities
@app.get("/commodities")
def commodities():
    """API endpoint that returns all available commodities."""
    return get_commodities()


# Returns available districts
@app.get("/districts")
def districts():
    """API endpoint that returns all available districts."""
    return get_districts()


# Returns markets for a given district
@app.get("/markets")
def markets(district: str):
    """API endpoint returning markets for the provided district.

    Args:
        district: District name to query markets for.

    Returns:
        List of market names.
    """
    return get_markets(district)