
from agmarknet_loader import get_commodity_data, get_all_commodities, get_all_districts, get_markets_by_district
from db import get_connection
CSV_FILE = "Daily Price Arrival Report-03-06-2026 to 03-06-2026 for Maharashtra.csv"


# Return price records for a commodity, optionally filtered
def get_prices(commodity, district=None, market=None):
    """Retrieve price rows for a commodity with optional filters.

    Args:
        commodity: Commodity name to query.
        district: Optional district name to filter results.
        market: Optional market name to filter results.

    Returns:
        List of dicts containing `District`, `Market`, `Min Price`,
        `Max Price` and `Modal Price`, or a message when no data found.
    """
    data = get_commodity_data(CSV_FILE, commodity, district, market)

    if data.empty:
        return {"message": f"No data found for commodity: {commodity}"}

    return data[
        [
            "District",
            "Market",
            "Min Price",
            "Max Price",
            "Modal Price"
        ]
    ].to_dict(orient="records")


# Return summary statistics for a commodity across markets
def get_summary(commodity, district=None, market=None):
    """Compute simple statistics (average/high/low) for modal prices.

    Args:
        commodity: Commodity name to summarize.
        district: Optional district to restrict the summary.
        market: Optional market to restrict the summary.

    Returns:
        Dict containing commodity, district, total_markets, average_modal_price,
        highest_modal_price and lowest_modal_price, or a message on no data.
    """
    data = get_commodity_data(CSV_FILE, commodity, district, market)

    if data.empty:
        return {"message": f"No data found for commodity: {commodity}"}

    # Convert modal prices from strings like "1,200.00" to floats
    modal_prices = (
        data["Modal Price"]
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    return {
        "commodity": commodity,
        "district": district,
        "total_markets": len(data),
        "average_modal_price": round(modal_prices.mean(), 2),
        "highest_modal_price": modal_prices.max(),
        "lowest_modal_price": modal_prices.min()
    }


# Returns all available commodities in the dataset
def get_commodities():
    """Return sorted list of available commodities in the CSV.

    Returns:
        List of commodity names.
    """
    return get_all_commodities(CSV_FILE)


# Returns all available districts in the dataset
def get_districts():
    """Return sorted list of available districts in the CSV.

    Returns:
        List of district names.
    """
    return get_all_districts(CSV_FILE)


# Returns markets for a selected district
def get_markets(district):
    """Return sorted list of markets for the given district.

    Args:
        district: District name to filter markets by.

    Returns:
        List of market names.
    """
    return get_markets_by_district(CSV_FILE, district)

def get_top_markets(commodity, limit=5):
    data = get_commodity_data(CSV_FILE, commodity)

    if data.empty:
        return {"message": f"No data found for commodity: {commodity}"}

    data = data.copy()

    data["Modal Price"] = (
        data["Modal Price"]
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    top_markets = data.sort_values(
        by="Modal Price",
        ascending=False
    )

    return top_markets[
        ["Market", "District", "Modal Price"]
    ].head(limit).to_dict(orient="records")

def get_dashboard(commodity):
    data = get_commodity_data(CSV_FILE, commodity)

    if data.empty:
        return {"message": f"No data found for commodity: {commodity}"}

    data = data.copy()

    data["Modal Price"] = (
        data["Modal Price"]
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    highest = data.loc[data["Modal Price"].idxmax()]
    lowest = data.loc[data["Modal Price"].idxmin()]

    return {
        "commodity": commodity,
        "highest_market": highest["Market"],
        "highest_price": highest["Modal Price"],
        "lowest_market": lowest["Market"],
        "lowest_price": lowest["Modal Price"],
        "average_price": round(data["Modal Price"].mean(), 2),
        "total_markets": len(data)
    }

def get_commodities_from_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM commodities
        ORDER BY name;
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row[0] for row in rows]