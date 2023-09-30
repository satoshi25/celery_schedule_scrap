from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DisconnectionError
from dotenv import load_dotenv

import os
import logging

load_dotenv()


def handle_disconnect(dbapi_connection, connection_record):
    if dbapi_connection is not None:
        try:
            dbapi_connection.ping(reconnect=True)
        except Exception as e:
            logging.error(f"Database disconnection error: {e}, Connection record: {connection_record}")
            raise DisconnectionError("Could not reconnect: %s" % e)


DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL, echo=True)

event.listen(engine, 'handle_error', handle_disconnect)

SessionFactory = sessionmaker(autoflush=False, autocommit=False, bind=engine)
