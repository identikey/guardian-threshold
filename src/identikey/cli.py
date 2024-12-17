import argparse
import os  # Import os to set environment variables
from identikey.server import start
import threshold_crypto as tc
import subprocess
from identikey.dkg_orchestrator import perform_dkg  # Add this import


def main():
    parser = argparse.ArgumentParser(description="Threshold Cryptography CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Encrypt command
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a message")
    encrypt_parser.add_argument("message", type=str, help="Message to encrypt")

    # Decrypt command
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a message")
    decrypt_parser.add_argument(
        "encrypted_message", type=str, help="Message to decrypt"
    )
    decrypt_parser.add_argument(
        "--shares",
        type=int,
        nargs="+",
        required=True,
        help="Participant share indices for decryption",
    )

    dkg_parser = subparsers.add_parser("dkg", help="Distributed Key Generation")
    dkg_parser.add_argument(
        "urls",
        type=str,
        nargs="+",
        help="Participant URLs for DKG",
    )
    dkg_parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        required=True,
        help="Threshold number for DKG",
    )
    dkg_parser.add_argument(
        "-n",
        "--total",
        type=int,
        help="Total number of participants (optional, defaults to number of URLs)",
    )

    # Add run-server command
    run_server_parser = subparsers.add_parser(
        "run-server", help="Run the keyholder server"
    )
    run_server_parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port to run the server on",
    )
    run_server_parser.add_argument(
        "--db",  # New argument for database file
        type=str,
        default="data/keyholder.db",
        help="Database file to use",
    )

    # Add migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Run database migrations")
    migrate_parser.add_argument(
        "--db",
        type=str,
        default="data/keyholder.db",
        help="Database file to migrate",
    )
    migrate_parser.add_argument(
        "alembic_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass to Alembic, e.g. upgrade head",
    )

    args = parser.parse_args()

    if args.command == "dkg":
        n = args.total if args.total is not None else len(args.urls)
        if n != len(args.urls):
            raise ValueError("Please pass in a URL for each participant")
        if args.threshold > n:
            raise ValueError("Threshold must not exceed the number of participants")

        perform_dkg(args.urls, args.threshold, n)
    elif args.command == "encrypt":
        # Example parameter generation
        curve_params = tc.CurveParameters()
        thresh_params = tc.ThresholdParameters(t=3, n=5)
        pub_key, key_shares = tc.create_public_key_and_shares_centralized(
            curve_params, thresh_params
        )

        encrypted_message = tc.encrypt_message(args.message, pub_key)
        print(f"Encrypted message: {encrypted_message}")

    elif args.command == "decrypt":
        # Example parameter setup (should match encryption parameters)
        curve_params = tc.CurveParameters()
        thresh_params = tc.ThresholdParameters(t=3, n=5)

        # Placeholder for encrypted_message; in practice, this should be provided or loaded appropriately
        encrypted_message = args.encrypted_message

        # Gather the required key shares based on provided indices
        key_shares = [
            retrieve_share(index) for index in args.shares
        ]  # Implement retrieve_share accordingly

        partial_decryptions = [
            tc.compute_partial_decryption(encrypted_message, share)
            for share in key_shares
        ]
        decrypted_message = tc.decrypt_message(
            partial_decryptions, encrypted_message, thresh_params
        )
        print(f"Decrypted message: {decrypted_message}")

    elif args.command == "run-server":
        start(port=args.port, db_file=args.db)

    elif args.command == "migrate":
        db_url = f"sqlite:///./{args.db}"
        alembic_command = ["alembic", "-x", f"db_file={db_url}"] + args.alembic_args
        subprocess.run(alembic_command)


def retrieve_share(index):
    # Implement the logic to retrieve the key share based on the index
    # This could involve reading from a file, database, or another source
    pass


if __name__ == "__main__":
    main()
