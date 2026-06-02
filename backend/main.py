from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AgriPrice Backend Running"}

@app.get("/prices")
def get_prices():
    # This function will call the get_prices function from agmarknet.py
    from agmarknet import get_prices as fetch_prices
    prices = fetch_prices()
    return prices