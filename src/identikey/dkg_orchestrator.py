import json
import requests
import logging
from typing import List, Tuple, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_participants(participants: List[Tuple[str, str]], t: int, n: int):
    logger.info(
        f"Registering {len(participants)} participants with threshold {t} of {n}"
    )
    for pi, url in participants:
        for pj, _ in participants:
            if pj != pi:
                try:
                    response = requests.post(
                        f"{url}/register_participants",
                        json={
                            "participants": [p for p, _ in participants],
                            "self_id": pi,
                            # "threshold": t,
                            # "total": n,
                        },
                    )
                    response.raise_for_status()
                    logger.info(f"Registered participants with {url}")
                except requests.RequestException as e:
                    logger.error(f"Failed to register participants with {url}: {e}")


def generate_closed_commitments(participant_urls: List[str], t: int, n: int):
    logger.info(f"Generating closed commitments with threshold {t} of {n}")
    commitments = []
    for url in participant_urls:
        try:
            response = requests.post(
                f"{url}/generate_closed_commitment",
                json={"t": t, "n": n},
            )
            response.raise_for_status()
            logger.info(f"Closed commitment received from {url}")
            commitments.append(response.json()["commitment"])
        except requests.RequestException as e:
            logger.error(f"Failed to start DKG process on {url}: {e}")
    return commitments


def distribute_closed_commitments(
    participants: List[Tuple[str, str]], commitments: List[Dict[str, str]]
):
    logger.info(f"Distributing closed commitments to {len(participants)} participants")
    logger.info(commitments)
    for _, url in participants:
        try:
            response = requests.post(
                f"{url}/receive_closed_commitments",
                json={"commitments": [json.loads(c) for c in commitments]},
            )
            response.raise_for_status()
            logger.info(f"Closed commitments sent to {url}")
        except requests.RequestException as e:
            logger.error(f"Failed to send closed commitments to {url}: {e}")


def perform_dkg(participant_urls: List[str], t: int, n: int):
    logger.info(f"Starting DKG with {n} participants, threshold {t}")

    # Get the participant IDs from each participant
    participant_ids = [
        requests.get(url=f"{url}/get_id").json()["id"] for url in participant_urls
    ]
    participants = list(zip(participant_ids, participant_urls))

    register_participants(participants, t, n)

    closed_commitments = generate_closed_commitments(participant_urls, t, n)

    # Distribute closed commitments to all participants
    distribute_closed_commitments(participants, closed_commitments)

    logger.info("DKG orchestration completed")
