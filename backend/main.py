from agmarknet_loader import get_markets_by_district
from fastapi import FastAPI
from agmarknet import get_prices, get_summary, get_commodities, get_districts, get_markets

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AgriPrice Backend Running"}

@app.get("/prices")
def prices(commodity: str, district: str = None, market: str = None):
    return get_prices(commodity, district, market)

@app.get("/summary")
def summary(commodity:str, district:str = None, market:str = None):
    return get_summary(commodity, district, market)

@app.get("/commodities")
def commodities():
    return get_commodities()

@app.get("/districts")
def districts():
    return get_districts()

@app.get("/markets")
def markets(district: str):
    return get_markets(district)