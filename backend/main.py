from fastapi import FastAPI
from agmarknet import get_prices, get_summary, get_commodities, get_districts, get_markets, get_top_markets, get_dashboard
from agmarknet import get_commodities_from_db, get_markets_from_db, get_prices_from_db, get_summary_from_db, get_districts_from_db, get_top_markets_from_db, get_dashboard_from_db
from pydantic import BaseModel
from db import get_connection
from auth import hash_password, verify_password

app = FastAPI()


# Root health-check endpoint
@app.get("/")
def home():
    """Simple health-check returning running status."""
    return {"message": "AgriPrice Backend Running"}


# Returns price records for a commodity
@app.get("/prices")
def prices(commodity: str, district: str = None, market: str = None):
    """API endpoint returning price records for a commodity.

    Args:
        commodity: Commodity name to query.
        district: Optional district name to filter.
        market: Optional market name to filter.

    Returns:
        JSON-serializable list of price records or message dict.
    """
    return get_prices_from_db(commodity, district, market)


# Returns aggregated summary statistics for a commodity
@app.get("/summary")
def summary(commodity:str, district:str = None, market:str = None):
    """API endpoint returning modal price summary for a commodity.

    Args:
        commodity: Commodity name to summarize.
        district: Optional district to restrict summary.
        market: Optional market to restrict summary.

    Returns:
        JSON-serializable dictionary with summary statistics.
    """
    return get_summary_from_db(commodity, district, market)


# Returns available commodities
@app.get("/commodities")
def commodities():
    """API endpoint that returns all available commodities."""
    return get_commodities_from_db()


# Returns available districts
@app.get("/districts")
def districts():
    """API endpoint that returns all available districts."""
    return get_districts_from_db()


# Returns markets for a given district
@app.get("/markets")
def markets(district: str):
    """API endpoint returning markets for the provided district.

    Args:
        district: District name to query markets for.

    Returns:
        List of market names.
    """
    return get_markets_from_db(district)


@app.get("/top-markets")
def top_markets(
    commodity: str,
    limit: int = 5
):
    return get_top_markets_from_db(
        commodity,
        limit
    )

@app.get("/dashboard")
def dashboard(commodity: str):
    return get_dashboard_from_db(commodity)


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class FavoriteRequest(BaseModel):
    user_id: int
    commodity: str


def ensure_favorites_table(cursor):
    """Create the favorites table if it does not already exist."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            commodity_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (user_id, commodity_name)
        )
        """
    )

# Registers a new user after checking for an existing email
@app.post("/register")
def register(user: RegisterRequest):
    """Create a new user account.

    Args:
        user: Registration payload with username, email, and password.

    Returns:
        Message indicating whether the user was created or already exists.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE email = %s
        """,
        (user.email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()

        return {
            "message": "Email already registered"
        }

    password_hash = hash_password(user.password)

    cursor.execute(
        """
        INSERT INTO users (
            username,
            email,
            password_hash
        )
        VALUES (%s, %s, %s)
        """,
        (
            user.username,
            user.email,
            password_hash
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "User registered successfully"
    }


# Authenticates a user by verifying the stored password hash
@app.post("/login")
def login(user: LoginRequest):
    """Authenticate a user using email and password.

    Args:
        user: Login payload with email and password.

    Returns:
        User details on success or an error message on failure.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, email, password_hash
        FROM users
        WHERE email = %s
        """,
        (user.email,)
    )

    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.close()
        conn.close()

        return {
            "message": "Invalid email or password"
        }

    user_id, username, email, password_hash = existing_user

    if not verify_password(user.password, password_hash):
        cursor.close()
        conn.close()

        return {
            "message": "Invalid email or password"
        }

    cursor.close()
    conn.close()

    return {
        "message": "Login successful",
        "user": {
            "id": user_id,
            "username": username,
            "email": email
        }
    }


# Adds a commodity to a user's favorites list
@app.post("/favorites")
def add_favorite(favorite: FavoriteRequest):
    """Add a commodity to a user's favorites.

    Args:
        favorite: Payload containing the user ID and commodity name.

    Returns:
        Message indicating whether the favorite was added or already exists.
    """

    conn = get_connection()
    cursor = conn.cursor()

    ensure_favorites_table(cursor)

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE id = %s
        """,
        (favorite.user_id,)
    )

    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.close()
        conn.close()

        return {
            "message": "User not found"
        }

    cursor.execute(
        """
        SELECT id
        FROM favorites
        WHERE user_id = %s
        AND commodity_name = %s
        """,
        (favorite.user_id, favorite.commodity)
    )

    existing_favorite = cursor.fetchone()

    if existing_favorite:
        cursor.close()
        conn.close()

        return {
            "message": "Favorite already exists"
        }

    cursor.execute(
        """
        INSERT INTO favorites (
            user_id,
            commodity_name
        )
        VALUES (%s, %s)
        """,
        (
            favorite.user_id,
            favorite.commodity
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Favorite added successfully"
    }


# Returns the favorite commodities for a user
@app.get("/favorites")
def get_favorites(user_id: int):
    """Get all favorite commodities for a user.

    Args:
        user_id: ID of the user whose favorites should be returned.

    Returns:
        List of favorite commodity names.
    """

    conn = get_connection()
    cursor = conn.cursor()

    ensure_favorites_table(cursor)

    cursor.execute(
        """
        SELECT commodity_name
        FROM favorites
        WHERE user_id = %s
        ORDER BY id DESC
        """,
        (user_id,)
    )

    favorites = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row[0] for row in favorites]


# Removes a commodity from a user's favorites list
@app.delete("/favorites")
def remove_favorite(favorite: FavoriteRequest):
    """Remove a commodity from a user's favorites.

    Args:
        favorite: Payload containing the user ID and commodity name.

    Returns:
        Message indicating whether the favorite was removed or not found.
    """

    conn = get_connection()
    cursor = conn.cursor()

    ensure_favorites_table(cursor)

    cursor.execute(
        """
        DELETE FROM favorites
        WHERE user_id = %s
        AND commodity_name = %s
        """,
        (
            favorite.user_id,
            favorite.commodity
        )
    )

    deleted_rows = cursor.rowcount

    conn.commit()

    cursor.close()
    conn.close()

    if deleted_rows == 0:
        return {
            "message": "Favorite not found"
        }

    return {
        "message": "Favorite removed successfully"
    }


@app.post("/logout")
def logout():
    return {
        "message": "Logged out successfully"
    }