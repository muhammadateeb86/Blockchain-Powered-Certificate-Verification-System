import mysql.connector
from config import MYSQL_CONFIG

def get_db_connection():
    """Establish and return a new database connection."""
    return mysql.connector.connect(**MYSQL_CONFIG)

def execute_query(query, params=None, fetchone=False):
    """
    Execute an SQL query safely.
    
    - If it's a SELECT query, fetches results automatically.
    - If `fetchone=True`, returns a single row.
    - If `fetchone=False`, returns all rows for SELECT queries.
    - For INSERT, UPDATE, DELETE, returns last inserted ID or affected rows.
    """
    conn = None
    cursor = None
    result = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())  # Ensure params is never None

        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchone() if fetchone else cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()  # Rollback on error
        print(f"Database Error: {err}")  # Log error
        raise Exception(f"Database error: {err}")  # Raise error for API to handle

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return result
