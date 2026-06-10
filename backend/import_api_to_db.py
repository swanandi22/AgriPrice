import requests
import time

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

if __name__ == "__main__":
    records = fetch_agmarknet_data(limit=50)

    print("Records fetched:", len(records))

    if records:
        print(records[0])