from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)

    integrations = relationship("CalendarIntegration", back_populates="user", cascade="all, delete")
