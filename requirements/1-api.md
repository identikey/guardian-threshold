# Project Overview
This project will be an API that orchestrates multiple machines to perform encryption and threshold decryption of sensitive information.
One machine will orchestrate things like DKG, the other machines each hold part of a secret.

# Tech stack
- poetry
- FastAPI
- SQLAlchemy, SQLite

# Feature Requirements
- install libraries using poetry
- make a `poetry run ..` command that spins up the API
- create a participants table, containing the custom id of each participant as well as primary key. 
  - it has open commitment, closed commitment
- make an initial api endpoint to check status of each box

# Relevant Docs



# Current file structure

THRESHOLD-CRYPTO
├── eval
├── identikey
│   ├── __pycache__
│   ├── cli.py
│   └── script.py
├── prompts
│   └── think.md
├── requirements
│   ├── _template.md
│   └── 1-api.md
├── test
│   ├── __init__.py
│   └── tests.py
├── threshold_crypto
│   ├── __pycache__
│   ├── __init__.py
│   ├── central.py
│   ├── data.py
│   ├── number.py
│   └── participant.py
├── .gitignore
├── .gitlab-ci.yml
├── LICENSE
├── poetry.lock
├── pyproject.toml
└── README.md