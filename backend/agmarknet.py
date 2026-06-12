
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


def get_markets_from_db(district):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT market_name
        FROM markets
        WHERE district = %s
        ORDER BY market_name
        """,
        (district,)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row[0] for row in rows]

def get_prices_from_db(commodity, district=None, market=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            m.district,
            m.market_name,
            dp.min_price,
            dp.max_price,
            dp.modal_price
        FROM daily_prices dp
        JOIN commodities c
            ON dp.commodity_id = c.id
        JOIN markets m
            ON dp.market_id = m.id
        WHERE c.name = %s
    """

    params = [commodity]

    if district:
        query += " AND m.district = %s"
        params.append(district)

    if market:
        query += " AND m.market_name = %s"
        params.append(market)

    cursor.execute(query, params)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "District": row[0],
            "Market": row[1],
            "Min Price": float(row[2]),
            "Max Price": float(row[3]),
            "Modal Price": float(row[4]),
        }
        for row in rows
    ]


def get_summary_from_db(commodity, district=None, market=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            AVG(dp.modal_price),
            MAX(dp.modal_price),
            MIN(dp.modal_price),
            COUNT(*)
        FROM daily_prices dp
        JOIN commodities c
            ON dp.commodity_id = c.id
        JOIN markets m
            ON dp.market_id = m.id
        WHERE c.name = %s
    """

    params = [commodity]

    if district:
        query += " AND m.district = %s"
        params.append(district)

    if market:
        query += " AND m.market_name = %s"
        params.append(market)

    cursor.execute(query, params)

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "commodity": commodity,
        "district": district,
        "market": market,
        "average_modal_price": round(float(result[0]), 2),
        "highest_modal_price": float(result[1]),
        "lowest_modal_price": float(result[2]),
        "total_markets": result[3]
    }


def get_districts_from_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT district
        FROM markets
        ORDER BY district
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row[0] for row in rows]


def get_top_markets_from_db(commodity, limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            m.market_name,
            m.district,
            dp.modal_price
        FROM daily_prices dp
        JOIN commodities c
            ON dp.commodity_id = c.id
        JOIN markets m
            ON dp.market_id = m.id
        WHERE c.name = %s
        ORDER BY dp.modal_price DESC
        LIMIT %s
        """,
        (commodity, limit)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "Market": row[0],
            "District": row[1],
            "Modal Price": float(row[2])
        }
        for row in rows
    ]


def get_dashboard_from_db(commodity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            m.market_name,
            dp.modal_price
        FROM daily_prices dp
        JOIN commodities c
            ON dp.commodity_id = c.id
        JOIN markets m
            ON dp.market_id = m.id
        WHERE c.name = %s
        ORDER BY dp.modal_price DESC
        LIMIT 1
        """,
        (commodity,)
    )

    highest = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            m.market_name,
            dp.modal_price
        FROM daily_prices dp
        JOIN commodities c
            ON dp.commodity_id = c.id
        JOIN markets m
            ON dp.market_id = m.id
        WHERE c.name = %s
        ORDER BY dp.modal_price ASC
        LIMIT 1
        """,
        (commodity,)
    )

    lowest = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            AVG(dp.modal_price),
            COUNT(*)
        FROM daily_prices dp
        JOIN commodities c
            ON dp.commodity_id = c.id
        WHERE c.name = %s
        """,
        (commodity,)
    )

    stats = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "commodity": commodity,
        "highest_market": highest[0],
        "highest_price": float(highest[1]),
        "lowest_market": lowest[0],
        "lowest_price": float(lowest[1]),
        "average_price": round(float(stats[0]), 2),
        "total_markets": stats[1]
    }


def get_historical_prices_from_db(commodity, market):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            dp.arrival_date,
            AVG(dp.modal_price)
        FROM daily_prices dp
        JOIN commodities c
            ON dp.commodity_id = c.id
        JOIN markets m
            ON dp.market_id = m.id
        WHERE c.name = %s
        AND m.market_name = %s
        GROUP BY dp.arrival_date
        ORDER BY dp.arrival_date
        """,
        (commodity, market)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "date": row[0],
            "modal_price": float(row[1])
        }
        for row in rows
    ]