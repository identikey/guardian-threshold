import logging
import random
import uvicorn
from typing import Any, Generator, List, Dict
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import init_db
import models
from pydantic import BaseModel
import threshold_crypto as tc
from threshold_crypto.data import CurveParameters, ThresholdParameters

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


@app.post("/register_participants")
def register_participants(
    participant_list: ParticipantList, db: Session = Depends(get_db)
):
    for participant_id in participant_list.participants:
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


@app.get("/participants")
def get_all_participants(
    db: Session = Depends(get_db),
) -> Dict[str, List[Dict[str, Any]]]:
    participants = db.query(models.Participant).all()
    return {
        "participants": [
            {"participant_id": p.participant_id, "is_self": p.is_self}
            for p in participants
        ]
    }


# Add this new class for the request body
class CommitmentRequest(BaseModel):
    t: int
    n: int


@app.post("/generate_closed_commitment")
def generate_closed_commitment(
    request: CommitmentRequest, db: Session = Depends(get_db)
):

    threshold_parameters = ThresholdParameters(request.t, request.n)
    curve_parameters = CurveParameters()

    me = db.query(models.Participant).filter_by(is_self=True).first()
    if not me:
        raise HTTPException(status_code=404, detail="Self participant not found")

    all_participants = db.query(models.Participant).all()
    all_participant_ids = [p.participant_id for p in all_participants]

    participant = tc.participant.Participant(
        me.participant_id,
        all_participant_ids,
        curve_parameters,
        threshold_parameters,
    )

    commitment = participant.closed_commitment()
    commitment_json = commitment.to_json()
    logger.info(f"Generated closed commitment: {commitment_json}")
    return {"participant_id": me.participant_id, "commitment": commitment_json}


if __name__ == "__main__":
    start()
