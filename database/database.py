import sqlite3
from pathlib import Path
import hashlib
import secrets
import bcrypt

# Database file location
DATABASE_PATH = Path(__file__).parent / "weather_outfit.db"


def get_connection():
    """Create and return a database connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create all required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        question_id INTEGER,
        answer_hash TEXT
    )
""")

    # Weather records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            wind_speed REAL NOT NULL,
            rain INTEGER NOT NULL DEFAULT 0,
            season TEXT NOT NULL,
            weather_condition TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # Outfit recommendations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            weather_id INTEGER,
            outfit_category TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            model_name TEXT NOT NULL DEFAULT 'Random Forest',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,
            FOREIGN KEY (weather_id)
                REFERENCES weather_records(id)
                ON DELETE SET NULL
        )
    """)

    # Favorite recommendations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recommendation_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, recommendation_id),
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,
            FOREIGN KEY (recommendation_id)
                REFERENCES recommendations(id)
                ON DELETE CASCADE
        )
    """)


    # User trip/outfit plans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outfit_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            destination TEXT NOT NULL,
            plan_date TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            occasion TEXT NOT NULL,
            style TEXT NOT NULL,
            temperature REAL,
            humidity REAL,
            wind_speed REAL,
            precipitation REAL,
            weather_code INTEGER,
            season TEXT,
            weather_condition TEXT,
            outfit_category TEXT,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'info',
            is_read INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    connection.commit()
        # Add security-question columns to older databases
    try:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN question_id INTEGER
        """)
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN answer_hash TEXT
        """)
    except sqlite3.OperationalError:
        pass

    connection.commit()
    connection.close()


def hash_password(password, salt=None):
    """Securely hash a password using PBKDF2."""

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000
    ).hex()

    return password_hash, salt


def verify_password(password, stored_hash, salt):
    """Verify a password against its stored hash."""

    password_hash, _ = hash_password(password, salt)

    return secrets.compare_digest(
        password_hash,
        stored_hash
    )


def create_user(username, password, question_id=None, answer=None):

    if not username or not password:
        return False, "fill_fields"

    if len(password) < 6:
        return False, "weak_password"

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    answer_hash = None

    # Security question is optional for new accounts
    if question_id is not None and answer:
        answer_hash = bcrypt.hashpw(
            answer.strip().lower().encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
    INSERT INTO users
    (
        username,
        password_hash,
        password_salt,
        question_id,
        answer_hash,
        role
    )
    VALUES (?, ?, ?, ?, ?, 'user')
""", (
    username,
    password_hash,
    "bcrypt",
    question_id,
    answer_hash
))

        connection.commit()

        return True, None

    except sqlite3.IntegrityError:

        return False, "username_taken"

    finally:

        connection.close()

def get_user(username):
    """Get user information."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = ?
    """, (username.strip(),))

    user = cursor.fetchone()

    connection.close()

    if user:
        return dict(user)

    return None

def authenticate_user(username, password):

    user = get_user(username)

    if not user:
        return None

    try:

        # ------------------------------------------
        # NEW USERS - BCRYPT
        # ------------------------------------------

        if user["password_salt"] == "bcrypt":

            valid = bcrypt.checkpw(
                password.encode("utf-8"),
                user["password_hash"].encode("utf-8")
            )

            if valid:
                return user

            return None

        # ------------------------------------------
        # OLD USERS - PBKDF2
        # ------------------------------------------

        valid = verify_password(
            password,
            user["password_hash"],
            user["password_salt"]
        )

        if not valid:
            return None

        # ------------------------------------------
        # MIGRATE OLD PASSWORD TO BCRYPT
        # ------------------------------------------

        new_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE users
            SET password_hash = ?,
                password_salt = ?
            WHERE id = ?
        """, (
            new_hash,
            "bcrypt",
            user["id"]
        ))

        connection.commit()
        connection.close()

        # Update returned user information
        user["password_hash"] = new_hash
        user["password_salt"] = "bcrypt"

        return user

    except Exception:
        return None

    if valid:
        return user

    return None

def save_weather(
    user_id,
    temperature,
    humidity,
    wind_speed,
    rain,
    season,
    weather_condition
):
    """Save weather information."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO weather_records
        (
            user_id,
            temperature,
            humidity,
            wind_speed,
            rain,
            season,
            weather_condition
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        temperature,
        humidity,
        wind_speed,
        int(rain),
        season,
        weather_condition
    ))

    weather_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return weather_id


def save_recommendation(
    user_id,
    weather_id,
    outfit_category,
    recommendation,
    model_name="Random Forest"
):
    """Save an outfit recommendation."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO recommendations
        (
            user_id,
            weather_id,
            outfit_category,
            recommendation,
            model_name
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        weather_id,
        outfit_category,
        recommendation,
        model_name
    ))

    recommendation_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return recommendation_id


def get_user_recommendations(user_id):
    """Return recommendation history for a user."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.*,
            w.temperature,
            w.humidity,
            w.wind_speed,
            w.rain,
            w.season,
            w.weather_condition
        FROM recommendations r
        LEFT JOIN weather_records w
            ON r.weather_id = w.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def add_favorite(user_id, recommendation_id):
    """Add a recommendation to favorites."""

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO favorites
            (
                user_id,
                recommendation_id
            )
            VALUES (?, ?)
        """, (
            user_id,
            recommendation_id
        ))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def get_user_favorites(user_id):
    """Return favorite recommendations."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.*,
            f.created_at AS favorite_date
        FROM favorites f
        JOIN recommendations r
            ON f.recommendation_id = r.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_statistics():
    """Return basic system statistics."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM weather_records")
    weather_records = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM recommendations")
    recommendations = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM favorites")
    favorites = cursor.fetchone()[0]

    connection.close()

    return {
        "users": users,
        "weather_records": weather_records,
        "recommendations": recommendations,
        "favorites": favorites
    }


# Initialize database when the module is loaded
initialize_database()

def get_all_users():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            role,
            created_at
        FROM users
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]

def update_user_role(user_id, role):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET role = ?
        WHERE id = ?
    """, (
        role,
        user_id
    ))

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated
# --------------------------------------------------
# FORGOT PASSWORD
# --------------------------------------------------

def get_security_question(username):

    user = get_user(username)

    if not user:
        return None

    question_id = user.get("question_id")

    if question_id is None:
        return None

    return question_id


def verify_security_answer(username, answer):

    user = get_user(username)

    if not user:
        return False

    answer_hash = user.get("answer_hash")

    if not answer_hash:
        return False

    try:
        return bcrypt.checkpw(
            answer.strip().lower().encode("utf-8"),
            answer_hash.encode("utf-8")
        )
    except Exception:
        return False


def reset_password(username, new_password):

    if not new_password:
        return False

    if len(new_password) < 6:
        return False

    user = get_user(username)

    if not user:
        return False

    new_hash = bcrypt.hashpw(
        new_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET password_hash = ?,
            password_salt = ?
        WHERE username = ?
    """, (
        new_hash,
        "bcrypt",
        username.strip()
    ))

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


def create_outfit_plan(user_id, destination, plan_date, departure_time,
                       occasion, style, weather, season, condition,
                       outfit_category, recommendation):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO outfit_plans (
            user_id, destination, plan_date, departure_time, occasion, style,
            temperature, humidity, wind_speed, precipitation, weather_code,
            season, weather_condition, outfit_category, recommendation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, destination, plan_date, departure_time, occasion, style,
          weather.get("temperature"), weather.get("humidity"),
          weather.get("wind_speed"), weather.get("precipitation"),
          weather.get("weather_code"), season, condition,
          outfit_category, recommendation))
    plan_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return plan_id


def get_user_plans(user_id, limit=50):
    connection = get_connection()
    rows = connection.execute("""
        SELECT * FROM outfit_plans
        WHERE user_id=?
        ORDER BY plan_date ASC, departure_time ASC
        LIMIT ?
    """, (user_id, limit)).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def delete_user_plan(user_id, plan_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM outfit_plans WHERE id=? AND user_id=?",
                   (plan_id, user_id))
    connection.commit()
    deleted = cursor.rowcount > 0
    connection.close()
    return deleted


def create_notification(user_id, title, message, severity="info"):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO notifications (user_id, title, message, severity)
        VALUES (?, ?, ?, ?)
    """, (user_id, title, message, severity))
    notification_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return notification_id


def get_user_notifications(user_id, unread_only=False, limit=100):
    connection = get_connection()
    query = "SELECT * FROM notifications WHERE user_id=?"
    params = [user_id]
    if unread_only:
        query += " AND is_read=0"
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    rows = connection.execute(query, params).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def mark_notification_read(user_id, notification_id=None):
    connection = get_connection()
    if notification_id is None:
        connection.execute("UPDATE notifications SET is_read=1 WHERE user_id=?",
                           (user_id,))
    else:
        connection.execute(
            "UPDATE notifications SET is_read=1 WHERE user_id=? AND id=?",
            (user_id, notification_id))
    connection.commit()
    connection.close()
