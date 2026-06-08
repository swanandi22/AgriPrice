import pandas as pd

# Load CSV and normalize header row into DataFrame columns
def load_agmarknet_data(file_path):
    """Load Agmarknet CSV and set the first row as headers.

    Args:
        file_path: Path to the Agmarknet CSV file.

    Returns:
        pandas.DataFrame with the header row applied, or None on error.
    """
    try:
        df = pd.read_csv(file_path)
        df.columns = df.iloc[0] #Setting the first row as header
        df = df[1:] # Removing the first row which is now the header
        return df
    except Exception as e:
        # Keep error handling minimal; caller should handle None result
        print(f"Error loading data: {e}")
        return None


# Return rows matching a commodity and optional district/market
def get_commodity_data(file_path, commodity, district=None, market=None):
    """Filter DataFrame rows for a commodity and optional filters.

    Args:
        file_path: Path to the Agmarknet CSV file.
        commodity: Commodity name to filter by.
        district: Optional district name to further filter.
        market: Optional market name to further filter.

    Returns:
        pandas.DataFrame containing matching rows (may be empty).
    """
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


# Returns a sorted list of distinct commodity names
def get_all_commodities(file_path):
    """Get all unique commodities from the CSV.

    Args:
        file_path: Path to the Agmarknet CSV file.

    Returns:
        Sorted list of commodity names.
    """
    df = load_agmarknet_data(file_path)
    commodities = df["Commodity"].unique()
    return sorted(commodities.tolist())


# Returns a sorted list of distinct district names
def get_all_districts(file_path):
    """Get all unique districts from the CSV.

    Args:
        file_path: Path to the Agmarknet CSV file.

    Returns:
        Sorted list of district names.
    """
    df = load_agmarknet_data(file_path)
    districts = df["District"].unique()
    return sorted(districts.tolist())


# Return markets available within a district
def get_markets_by_district(file_path, district):
    """Get all unique markets for a given district.

    Args:
        file_path: Path to the Agmarknet CSV file.
        district: District name to filter markets by.

    Returns:
        Sorted list of market names belonging to the district.
    """
    df = load_agmarknet_data(file_path)
    filtered_data = df[df["District"] == district]
    markets = filtered_data["Market"].unique()
    return sorted(markets.tolist())