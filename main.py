import logging
import random
import uvicorn
from typing import Any, Generator, List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import init_db
import models
from pydantic import BaseModel

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# These will be set up later
engine = None
SessionLocal = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/status")
def read_status() -> dict[str, str]:
    return {"status": "OK"}


@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    check_or_create_self_participant(db)


def check_or_create_self_participant(db: Session):
    self_participant = db.query(models.Participant).filter_by(is_self=True).first()

    if self_participant:
        logger.info(
            f"Existing self participant found with ID: {self_participant.participant_id}"
        )
    else:
        new_id = random.randint(1, 100000000)
        logger.info(f"Creating a new self for key generation with ID: {new_id}")
        db.add(models.Participant(participant_id=new_id, is_self=True))
        db.commit()


def start(port: int = 8000, db_file: str = "keyholder.db") -> None:
    global engine, SessionLocal
    engine, SessionLocal = init_db(db_file)
    models.Base.metadata.create_all(bind=engine)

    uvicorn.run(app, host="0.0.0.0", port=port)


class ParticipantList(BaseModel):
    participants: List[int]
    self_id: int


@app.post("/register_participants")
def register_participants(
    participant_list: ParticipantList, db: Session = Depends(get_db)
):
    # Register self
    self_participant = db.query(models.Participant).filter_by(is_self=True).first()
    if self_participant:
        self_participant.participant_id = participant_list.self_id
    else:
        self_participant = models.Participant(
            participant_id=participant_list.self_id, is_self=True
        )
        db.add(self_participant)

    # Register other participants
    for participant_id in participant_list.participants:
        if participant_id != participant_list.self_id:
            existing = (
                db.query(models.Participant)
                .filter_by(participant_id=participant_id)
                .first()
            )
            if not existing:
                new_participant = models.Participant(participant_id=participant_id)
                db.add(new_participant)
    db.commit()
    return {"status": "Participants registered"}


@app.post("/start_dkg")
def start_dkg(db: Session = Depends(get_db)):
    # Here you would implement the actual DKG logic
    # This is a placeholder for now
    return {"status": "DKG process started"}


@app.get("/get_id")
def get_id(db: Session = Depends(get_db)):
    self_participant = db.query(models.Participant).filter_by(is_self=True).first()
    if not self_participant:
        raise HTTPException(status_code=404, detail="Self participant not found")
    return {"id": self_participant.participant_id}


if __name__ == "__main__":
    start()
