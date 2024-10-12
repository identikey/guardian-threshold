import requests
import logging
from typing import List
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def perform_dkg(participant_urls: List[str]):
    logger.info(f"Starting DKG with {len(participant_urls)} participants")

    # Get the participant IDs from each participant
    participant_ids = [
        requests.get(url=f"{url}/get_id").json()["id"] for url in participant_urls
    ]
    print(participant_ids)

    # Step 1: Inform all participants about each other's IDs
    for url, participant_id in zip(participant_urls, participant_ids):
        try:
            response = requests.post(
                f"{url}/register_participants",
                json={"participants": participant_ids, "self_id": participant_id},
            )
            response.raise_for_status()
            logger.info(f"Registered participants with {url}")
        except requests.RequestException as e:
            logger.error(f"Failed to register participants with {url}: {e}")

    # Step 2: Trigger DKG process
    for url in participant_urls:
        try:
            response = requests.post(f"{url}/start_dkg")
            response.raise_for_status()
            logger.info(f"Started DKG process on {url}")
        except requests.RequestException as e:
            logger.error(f"Failed to start DKG process on {url}: {e}")

    # Note: The actual DKG process will happen asynchronously on each participant's server.
    # You might want to add a way to check the status or wait for completion.

    logger.info("DKG orchestration completed")
