import csv
import os
import sqlite3
from restaurant import Restaurant

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "restaurants.db"
)


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Open (and implicitly create) the SQLite database file."""
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    return conn


def create_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            price_range TEXT NOT NULL,
            avg_price REAL NOT NULL,
            food_category TEXT NOT NULL,
            rating REAL NOT NULL,
            review_count INTEGER NOT NULL DEFAULT 0,
            special_features TEXT
        )
    """)

    conn.commit()


def add_restaurant(
    conn: sqlite3.Connection,
    r: Restaurant
) -> None:

    conn.execute("""
        INSERT INTO restaurants (
            id,
            name,
            location,
            price_range,
            avg_price,
            food_category,
            rating,
            review_count,
            special_features
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        r.id,
        r.name,
        r.location,
        r.price_range,
        r.avg_price,
        r.food_category,
        r.rating,
        r.review_count,
        ";".join(r.special_features)
    ))

    conn.commit()


def edit_restaurant(
    conn: sqlite3.Connection,
    restaurant_id: int,
    **fields
) -> int:
    """Update one or more whitelisted fields and return rows changed."""

    if not fields:
        return 0

    allowed = {
        "name",
        "location",
        "price_range",
        "avg_price",
        "food_category",
        "rating",
        "review_count",
        "special_features"
    }

    unknown = set(fields) - allowed

    if unknown:
        raise ValueError(
            f"Unknown restaurant field(s): "
            f"{', '.join(sorted(unknown))}"
        )

    values = []
    assignments = []

    for column, value in fields.items():

        if column == "special_features":

            if isinstance(value, list):
                value = ";".join(value)

            elif value is None:
                value = ""

        assignments.append(f"{column} = ?")
        values.append(value)

    values.append(restaurant_id)

    cursor = conn.execute(
        f"""
        UPDATE restaurants
        SET {', '.join(assignments)}
        WHERE id = ?
        """,
        values
    )

    conn.commit()

    return cursor.rowcount


def get_all(
    conn: sqlite3.Connection
) -> list[Restaurant]:

    rows = conn.execute(
        "SELECT * FROM restaurants ORDER BY id"
    ).fetchall()

    return [
        _row_to_restaurant(row)
        for row in rows
    ]


def get_by_location(
    conn: sqlite3.Connection,
    location: str
) -> list[Restaurant]:

    rows = conn.execute(
        """
        SELECT *
        FROM restaurants
        WHERE lower(location) = lower(?)
        ORDER BY id
        """,
        (location,)
    ).fetchall()

    return [
        _row_to_restaurant(row)
        for row in rows
    ]


def get_locations(
    conn: sqlite3.Connection
) -> list[str]:

    rows = conn.execute(
        """
        SELECT DISTINCT location
        FROM restaurants
        ORDER BY location
        """
    ).fetchall()

    return [
        row["location"]
        for row in rows
    ]


def get_food_categories(
    conn: sqlite3.Connection
) -> list[str]:

    rows = conn.execute(
        """
        SELECT DISTINCT food_category
        FROM restaurants
        ORDER BY food_category
        """
    ).fetchall()

    return [
        row["food_category"]
        for row in rows
    ]


def _row_to_restaurant(
    row: sqlite3.Row
) -> Restaurant:

    features = (
        row["special_features"].split(";")
        if row["special_features"]
        else []
    )

    return Restaurant(
        id=row["id"],
        name=row["name"],
        location=row["location"],
        price_range=row["price_range"],
        avg_price=float(row["avg_price"]),
        food_category=row["food_category"],
        rating=float(row["rating"]),
        review_count=int(row["review_count"]),
        special_features=[
            f for f in features if f
        ],
    )


def _parse_features(
    raw: str
) -> list[str]:

    if not raw or not raw.strip():
        return []

    # The supplied dataset uses semicolons;
    # commas are accepted as a fallback.
    separator = ";" if ";" in raw else ","

    return [
        part.strip()
        for part in raw.split(separator)
        if part.strip()
    ]


def load_from_csv(
    conn: sqlite3.Connection,
    csv_path: str
) -> int:
    """Load all usable restaurant rows from the supplied CSV.

    Pending rows have no platform rating/review count. Instead of discarding
    them or inventing a quality score, their rating is set to the mean of the
    verified ratings and their review count is set to zero. In the Bayesian
    formula, v=0 therefore gives exactly the dataset mean, making an
    unverified restaurant neutral rather than artificially good or bad.
    """

    with open(
        csv_path,
        newline="",
        encoding="utf-8-sig"
    ) as f:

        rows = list(csv.DictReader(f))

    verified_ratings = []

    for row in rows:

        raw_rating = row.get(
            "rating",
            ""
        ).strip()

        if raw_rating:

            try:
                verified_ratings.append(
                    float(raw_rating)
                )

            except ValueError:
                continue

    if not verified_ratings:
        raise ValueError(
            "CSV contains no usable ratings for the Bayesian prior."
        )

    prior_mean = (
        sum(verified_ratings)
        / len(verified_ratings)
    )

    count = 0

    for row in rows:

        raw_rating = row.get(
            "rating",
            ""
        ).strip()

        raw_reviews = row.get(
            "review_count",
            ""
        ).strip()

        is_verified = bool(
            raw_rating and raw_reviews
        )

        if is_verified:

            try:
                rating = float(raw_rating)

                review_count = int(
                    float(
                        raw_reviews.replace(
                            ",",
                            ""
                        )
                    )
                )

            except ValueError:
                continue

        else:

            rating = prior_mean
            review_count = 0

        restaurant = Restaurant(
            id=int(row["id"]),
            name=row["name"].strip(),
            location=row["location"].strip(),
            price_range=row["price_range"].strip(),
            avg_price=float(
                row["avg_price_vnd"].replace(
                    ",",
                    ""
                )
            ),
            food_category=row["food_category"].strip(),
            rating=rating,
            review_count=review_count,
            special_features=_parse_features(
                row.get(
                    "special_features",
                    ""
                )
            ),
        )

        # Preserve manual edits if this loader is run again.
        exists = conn.execute(
            """
            SELECT 1
            FROM restaurants
            WHERE id = ?
            """,
            (restaurant.id,)
        ).fetchone()

        if exists:
            continue

        add_restaurant(
            conn,
            restaurant
        )

        count += 1

    return count


def get_mean_rating(
    conn: sqlite3.Connection
) -> float:

    row = conn.execute(
        """
        SELECT AVG(rating) AS mean_rating
        FROM restaurants
        """
    ).fetchone()

    return (
        row["mean_rating"]
        if row["mean_rating"] is not None
        else 0.0
    )
