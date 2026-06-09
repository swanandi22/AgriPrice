from db import get_connection
from agmarknet_loader import load_agmarknet_data

CSV_FILE = "Daily Price Arrival Report-03-06-2026 to 03-06-2026 for Maharashtra.csv"


def import_data():
    print("Loading CSV...")

    df = load_agmarknet_data(CSV_FILE)

    print(f"Loaded {len(df)} rows")

    conn = get_connection()
    cursor = conn.cursor()

    print("Connected to PostgreSQL")

    # Insert commodities
    commodities = df["Commodity"].unique()

    for commodity in commodities:
        cursor.execute(
            """
            INSERT INTO commodities (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            """,
            (commodity,)
        )

    conn.commit()
    print("Commodities inserted")

    # Insert markets
    unique_markets = df[
        ["Market", "District", "State"]
    ].drop_duplicates()

    for _, row in unique_markets.iterrows():
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
                row["Market"],
                row["District"],
                row["State"]
            )
        )

    conn.commit()
    print("Markets inserted")

    # Insert daily prices
    for _, row in df.iterrows():

        cursor.execute(
            """
            SELECT id
            FROM commodities
            WHERE name = %s
            """,
            (row["Commodity"],)
        )

        commodity_id = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT id
            FROM markets
            WHERE market_name = %s
            AND district = %s
            """,
            (
                row["Market"],
                row["District"]
            )
        )

        market_id = cursor.fetchone()[0]

        min_price = float(
            str(row["Min Price"]).replace(",", "")
        )

        max_price = float(
            str(row["Max Price"]).replace(",", "")
        )

        modal_price = float(
            str(row["Modal Price"]).replace(",", "")
        )

        arrival_quantity = float(
            str(row["Arrival Quantity"]).replace(",", "")
        )

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
                TO_DATE(%s, 'DD-MM-YYYY')
            )
            """,
            (
                commodity_id,
                market_id,
                min_price,
                max_price,
                modal_price,
                row["Price Unit"],
                arrival_quantity,
                row["Arrival Unit"],
                row["Arrival Date"]
            )
        )

    conn.commit()
    print("Prices inserted")

    cursor.execute("SELECT COUNT(*) FROM commodities")
    print("Commodities:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM markets")
    print("Markets:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM daily_prices")
    print("Daily Prices:", cursor.fetchone()[0])

    cursor.close()
    conn.close()

    print("Data imported successfully!")


if __name__ == "__main__":
    import_data()