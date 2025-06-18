from sqlalchemy.orm import sessionmaker
from . import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)