from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

db = create_engine()
Base = declarative_base()