from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    custom_id = Column(String, unique=True, index=True)
    open_commitment = Column(String)
    closed_commitment = Column(String)
    key_share = Column(String)
