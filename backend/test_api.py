import requests

API_KEY = "579b464db66ec23bdd0000018a1fd09c08444906593b3a30ddcd2bbe"

url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 1,
    "filters[commodity]": "Onion"
}

print("Sending request...")

response = requests.get(
    url,
    params=params,
    timeout=30,
    headers={
        "accept": "application/json"
    }
)

print("Status:", response.status_code)
print(response.text[:500])