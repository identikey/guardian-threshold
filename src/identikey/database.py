from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def init_db(db_file: str = "test.db"):
    global engine, SessionLocal

    SQLALCHEMY_DATABASE_URL = f"sqlite:///./{db_file}"
    print(f"Using database: {SQLALCHEMY_DATABASE_URL}")

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


# These will be initialized later
engine = None
SessionLocal = None
