
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


username = os.getenv('DB_USER')
password = os.getenv('DB_PASS')
host = os.getenv('DB_HOST', 'db')

database_url = f"postgresql+psycopg2://{username}:{password}@{host}:5432/customer_support"

# Create the SQLAlchemy engine
engine = create_engine(database_url, echo=True)

Session = sessionmaker(bind=engine)

