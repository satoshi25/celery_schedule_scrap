from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

import os

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL, echo=True)

SessionFactory = sessionmaker(autoflush=False, autocommit=False, bind=engine)
