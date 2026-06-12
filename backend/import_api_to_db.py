import requests
import time

from db import get_connection

API_KEY = "579b464db66ec23bdd0000018a1fd09c08444906593b3a30ddcd2bbe"


def fetch_agmarknet_data(limit=50, offset=0):
    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit,
        "offset": offset
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for attempt in range(3):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()

            return response.json()["records"]

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    return []


def import_live_data():

    # Fetch data FIRST
    records = fetch_agmarknet_data(limit=50)

    if not records:
        print("No records fetched.")
        return

    print(f"Fetched {len(records)} records")

    conn = get_connection()
    cursor = conn.cursor()


    for record in records:

        # Insert commodity
        cursor.execute(
            """
            INSERT INTO commodities (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            """,
            (record["commodity"],)
        )

        # Check if market already exists
        cursor.execute(
            """
            SELECT id
            FROM markets
            WHERE market_name = %s
            AND district = %s
            AND state = %s
            """,
            (
                record["market"],
                record["district"],
                record["state"]
            )
        )

        existing_market = cursor.fetchone()

        # Insert only if market doesn't exist
        if not existing_market:
            cursor.execute(
                """
                INSERT INTO markets (
                    market_name,
                    district,
                    state
                )
                VALUES (%s, %s, %s)
                """,
                (
                    record["market"],
                    record["district"],
                    record["state"]
                )
            )

        # Get commodity id
        cursor.execute(
            """
            SELECT id
            FROM commodities
            WHERE name = %s
            """,
            (record["commodity"],)
        )

        commodity_id = cursor.fetchone()[0]

        # Get market id
        cursor.execute(
            """
            SELECT id
            FROM markets
            WHERE market_name = %s
            AND district = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                record["market"],
                record["district"]
            )
        )

        market_id = cursor.fetchone()[0]

        # Insert daily price
        cursor.execute(
            """
            INSERT INTO daily_prices (
                commodity_id,
                market_id,
                min_price,
                max_price,
                modal_price,
                price_unit,
                arrival_quantity,
                arrival_unit,
                arrival_date
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,
                TO_DATE(%s, 'DD/MM/YYYY')
            )
            """,
            (
                commodity_id,
                market_id,
                record["min_price"],
                record["max_price"],
                record["modal_price"],
                "Rs/Quintal",
                None,
                None,
                record["arrival_date"]
            )
        )

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM commodities")
    commodities_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM markets")
    markets_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM daily_prices")
    prices_count = cursor.fetchone()[0]

    print(f"Commodities: {commodities_count}")
    print(f"Markets: {markets_count}")
    print(f"Daily Prices: {prices_count}")

    cursor.close()
    conn.close()

    print("Live data imported successfully!")


if __name__ == "__main__":
    import_live_data()