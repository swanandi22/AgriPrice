import pandas as pd

def load_agmarknet_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = df.iloc[0] #Setting the first row as header
        df = df[1:] # Removing the first row which is now the header
        return df
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    
def get_commodity_data(file_path, commodity, district=None, market=None):
    df = load_agmarknet_data(file_path)

    filtered_data = df[df["Commodity"] == commodity]

    if district:
        filtered_data = filtered_data[
            filtered_data["District"] == district
        ]
    if market:
        filtered_data = filtered_data[
            filtered_data["Market"] == market
        ]
    return filtered_data


def get_all_commodities(file_path):
    df = load_agmarknet_data(file_path)
    commodities = df["Commodity"].unique()
    return sorted(commodities.tolist())


def get_all_districts(file_path):
    df = load_agmarknet_data(file_path)
    districts = df["District"].unique()
    return sorted(districts.tolist())

def get_markets_by_district(file_path, district):
    df = load_agmarknet_data(file_path)
    filtered_data = df[df["District"] == district]
    markets = filtered_data["Market"].unique()
    return sorted(markets.tolist())