import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()  # reads the .env file

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

def test_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT PostGIS_Version();"))
        print("Connected! PostGIS version:", result.scalar())

if __name__ == "__main__":
    test_connection()