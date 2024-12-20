import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters
DB_HOST = "db"  # Use "db" when running in Docker
DB_USER = "postgres"
DB_PASS = "admin"
DB_NAME = "crud_app_db"

# SQL queries for table creation
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
"""

CREATE_STUDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    age INT NOT NULL
);
"""

def create_database():
    """
    Creates the database if it does not already exist.
    """
    conn = psycopg2.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Database '{DB_NAME}' created successfully!")
    except psycopg2.errors.DuplicateDatabase:
        print(f"Database '{DB_NAME}' already exists.")
    cur.close()
    conn.close()

def create_tables():
    """
    Creates the necessary tables in the database.
    """
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
    )
    cur = conn.cursor()
    cur.execute(CREATE_USERS_TABLE)
    cur.execute(CREATE_STUDENTS_TABLE)
    conn.commit()
    cur.close()
    conn.close()
    print("Tables created successfully!")

if __name__ == "__main__":
    create_database()
    create_tables()
