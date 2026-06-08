from agmarknet_loader import get_commodity_data, get_all_commodities, get_all_districts, get_markets_by_district

CSV_FILE = "Daily Price Arrival Report-03-06-2026 to 03-06-2026 for Maharashtra.csv"


def get_prices(commodity, district=None, market=None):
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


def get_summary(commodity, district=None, market=None):
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
def get_commodities():
    return get_all_commodities(CSV_FILE)

def get_districts():
    return get_all_districts(CSV_FILE)

def get_markets(district):
    return get_markets_by_district(CSV_FILE, district)