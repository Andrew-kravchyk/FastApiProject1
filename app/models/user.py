from app.db.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String)
    username = Column(String)
    hashed_password = Column(String)

    profile = relationship("Profile", uselist=False, back_populates="user")
