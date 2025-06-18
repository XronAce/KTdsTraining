from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class CalendarIntegration(Base):
    __tablename__ = "calendar_integrations"

    integration_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    provider = Column(String, nullable=False)
    username = Column(String)
    password = Column(String)
    access_token = Column(String)

    user = relationship("User", back_populates="integrations")