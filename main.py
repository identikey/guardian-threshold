import logging
import random
import uvicorn
from typing import Any, Generator
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine  # , init_db
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()  # Add this line to create the FastAPI app instance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def start(port: int = 8000) -> None:
    import uvicorn

    # from database import init_db

    # Initialize the database with the port number
    # init_db(port)

    # print("Getting db in start()")
    # db = next(get_db())
    # check_or_create_self_participant(db)

    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    start()
