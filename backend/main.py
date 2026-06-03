from fastapi import FastAPI
from agmarknet import get_prices

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AgriPrice Backend Running"}

@app.get("/prices")
def prices(commodity: str):
    return get_prices(commodity)