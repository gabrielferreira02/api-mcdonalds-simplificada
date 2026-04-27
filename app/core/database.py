from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from app.core.vars import DB_URL

db = create_engine(DB_URL)
Base = declarative_base()