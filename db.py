import mysql.connector
from mysql.connector import Error

def get_connection():
    """Return a new MySQL database connection."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="appuser",
            password="app_pass123",
            database="login_system",
            auth_plugin="mysql_native_password"
        )
        return conn
    except Error as e:
        print("Database connection error:", e)
        return None


def fetch_one(query, params=None):
    """Fetch a single record."""
    conn = get_connection()
    if conn is None:
        return None
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result
    except Error as e:
        print("Query error:", e)
        conn.close()
        return None


def fetch_all(query, params=None):
    """Fetch all records."""
    conn = get_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    except Error as e:
        print("Query error:", e)
        conn.close()
        return []


def execute(query, params=None):
    """Execute INSERT/UPDATE/DELETE."""
    conn = get_connection()
    if conn is None:
        return False
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print("Execution error:", e)
        conn.close()
        return False
