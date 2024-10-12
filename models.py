from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, unique=True, index=True)
    open_commitment = Column(String)
    closed_commitment = Column(String)
    key_share = Column(String)
    is_self = Column(Boolean, default=False)
