import threshold_crypto as tc
from threshold_crypto import participant
from threshold_crypto import central
from threshold_crypto.data import CurveParameters, ThresholdParameters
import random

# Set up parameters
curve_params = tc.CurveParameters()
thresh_params = tc.ThresholdParameters(t=3, n=5)

# Generate public key and shares
# pub_key, key_shares = tc.create_public_key_and_shares_centralized(curve_params, thresh_params)


####### DKG #######

tp = ThresholdParameters(3, 5)
cp = CurveParameters()
message = "Some secret message!!!!!"


# Generate random integer IDs for participants
def generate_random_id():
    return random.randint(10 ** (tp.n - 1), (10**tp.n) - 1)


participant_ids = [generate_random_id() for _ in range(tp.n)]
print(participant_ids)

participants = [
    participant.Participant(id, participant_ids, cp, tp) for id in participant_ids
]

# via broadcast
for pi in participants:
    for pj in participants:
        if pj != pi:
            closed_commitment = pj.closed_commmitment()
            pi.receive_closed_commitment(closed_commitment)

# via broadcast
for pi in participants:
    for pj in participants:
        if pj != pi:
            open_commitment = pj.open_commitment()
            pi.receive_open_commitment(open_commitment)


public_key = participants[0].compute_public_key()
# for pk in [p.compute_public_key() for p in participants[1:]]:
#     self.assertEqual(public_key, pk)

# via broadcast
for pi in participants:
    for pj in participants:
        if pj != pi:
            F_ij = pj.F_ij_value()
            pi.receive_F_ij_value(F_ij)

# SECRETLY from i to j
for pi in participants:
    for pj in participants:
        if pj != pi:
            s_ij = pj.s_ij_value_for_participant(pi.id)
            pi.receive_sij(s_ij)

shares = [p.compute_share() for p in participants]

# test encryption/decryption

em = central.encrypt_message(message, public_key)

pdms = [participant.compute_partial_decryption(em, ks) for ks in shares[: tp.t]]
dm = central.decrypt_message(pdms, em, tp)
print(dm)  # Should print "Secret message"


# # Encrypt a message
# message = "Secret message"
# encrypted_message = tc.encrypt_message(message, pub_key)

# # Compute partial decryptions (simulating 3 out of 5 participants)
# partial_decryptions = [
#     tc.compute_partial_decryption(encrypted_message, key_shares[i]) for i in [0, 2, 4]
# ]

# # Decrypt the message
# decrypted_message = tc.decrypt_message(
#     partial_decryptions, encrypted_message, thresh_params
# )

# print(decrypted_message)  # Should print "Secret message"
