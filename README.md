# Threshold Encryption


## High-level

1. Spin up multiple nodes
2. Do Distributed Key Generation between them
3. Use composite public key to generate an encrypted secret
4. Request a threshold of nodes to decrypt the secret

The CLI has the orchestrator which orchestrates between the running encryption nodes.

Persistance for each running process is handled via SQLite.

## How to use

### Run migrations

`uv run alembic` # TODO

## Credits

Special thanks to @tompeterson, who originally authored the excellent library for the El Gamal-based threshold cryptography.


## Threshold steps

### DKG (Distributed Key Generation) Phase:
1. **Setup**
   - Set threshold parameters (t=3, n=5)
   - Set curve parameters
   - Generate random IDs for participants

2. **Commitment Exchange** (2 rounds of broadcast)
   - Round 1: Each participant broadcasts their closed commitments
   - Round 2: Each participant broadcasts their open commitments

3. **Public Key Generation**
   - Compute the shared public key
   - All participants should arrive at the same public key

4. **Share Distribution**
   - Each participant broadcasts their F_ij values
   - Each participant secretly sends s_ij values to other participants
   - Each participant computes their final share

### Encryption/Decryption Process:
1. **Encryption**
   - Take a message and the public key
   - Use `central.encrypt_message()` to encrypt
   
2. **Decryption**
   - Collect partial decryptions from t participants (in this case, 3 out of 5)
   - Each participant computes their partial decryption using their share
   - Combine partial decryptions using `central.decrypt_message()`

The commented-out code at the bottom shows a simplified version of the same process using the higher-level `threshold_crypto` API.

Key Security Note: The s_ij values must be transmitted securely (privately) between participants, while other values can be broadcast publicly.

# Notes

The point_bytes are mapped randomly from the finite field of the elliptical curve and then hashed to derive the encryption key used to symmetrically encrypt the main ciphertext. Each individual participant comes together to form a single composite public key. 

when decrypting, each participant generates a partial decryption. These partial decryptions require access to the c1 value in the Encrypted message. the central party then combines the partial decryptions to derive the point bytes, which is the point within the Galois field. From there the symmetric decryption key is derived that can then decrypt the main ciphertext from at the point of the central party. 

Note that there appears to be a re-encryption mechanism built into this library, so explore that as a possibility for our proxy-recryption-service. 

# Corner Cases To Handle

During DKG, handle if a generated participant ID is a duplicate.

---

# Threshold cryptography library

A stateless library which offers functionality for ElGamal-based threshold decryption with centralized or distributed key generation.

Threshold decryption means a message can be encrypted using a simple public key, but for decryption at least t out of n
share owners must collaborate to decrypt the message.

A hybrid approach (using [pynacl](https://pynacl.readthedocs.io) for symmetric encryption and
[PyCryptodome](https://pycryptodome.readthedocs.io) for ECC operations) is used for message encryption and decryption.
Therefore there are no limitations regarding message lengths or format. Additionally the integrity of a message is
secured by using the AE-scheme, meaning changes to some parts of the ciphertext, to partial decryptions or even
dishonest share owners can be detected.

## Usage

Import the library:

    >>> import threshold_crypto as tc

### Parameter Generation

Generate required parameters:

    >>> curve_params = tc.CurveParameters()
    >>> thresh_params = tc.ThresholdParameters(t=3, n=5)

The `CurveParameters` describe the elliptic curve the operations are performed on.
The `ThresholdParameters` determine the number of created shares `n` and the number of required participants for the decryption operation `t`.

### Centralized Key Generation

The public key and shares of the private key can be computed in a centralized manner by a trusted third party:

    >>> pub_key, key_shares = tc.create_public_key_and_shares_centralized(curve_params, thresh_params)

### Distributed Key Generation

But they can also be computed via a distributed key generation (DKG) protocol following "A threshold cryptosystem without a trusted party" by Pedersen (1991).
This involves multiple steps performed by all participants in collaboration.
The following example code uses lists to illustrate this, but has to be distributed over the different participant applications and machines in practice.

The first step is the participant initialization:

    >>> participant_ids = list(range(1, thresh_params.n + 1))
    >>> participants = [tc.Participant(id, participant_ids, curve_params, thresh_params) for id in participant_ids]

Next each participant broadcasts a closed commitment to a share of the later public key to the other participants:

    >>> for pi in participants:
    ...     for pj in participants:
    ...         if pj != pi:
    ...             closed_commitment = pj.closed_commitment()
    ...             pi.receive_closed_commitment(closed_commitment)

After each participant has received all closed commitments they broadcast their open commitments:

    >>> for pi in participants:
    ...     for pj in participants:
    ...         if pj != pi:
    ...             open_commitment = pj.open_commitment()
    ...             pi.receive_open_commitment(open_commitment)

Afterwards each participant should be able to compute the same public key:

    >>> public_key = participants[0].compute_public_key()
    >>> for pk in [p.compute_public_key() for p in participants[1:]]:
    ...     assert public_key == pk

Now each participant broadcasts his F_ij (following the notation of Pedersen) values to all other participants.
These values are used to commit to the secret s_ij values send and received in the next step.

    >>> for pi in participants:
    ...     for pj in participants:
    ...         if pj != pi:
    ...             F_ij = pj.F_ij_value()
    ...             pi.receive_F_ij_value(F_ij)

Ongoing each participant sends a share of his private secret value to every other participant SECRETLY.
**Attention**: The library currently does NOT enforce this secrecy. Clients have to provide this functionality themselves.
This is heavily important and the protocol does not fulfill its security guarantees otherwise (meaning it is completely broken).

    >>> for pi in participants:
    ...     for pj in participants:
    ...         if pj != pi:
    ...             s_ij = pj.s_ij_value_for_participant(pi.id)
    ...             pi.receive_sij(s_ij)

Finally each participant can compute his `KeyShare`, which can be used for computing `PartialDecryption` or `PartialReEncryptionKey` objects.

    >>> shares = [p.compute_share() for p in participants]

### Encryption

A message is encrypted using the public key:

    >>> message = 'Some secret message to be encrypted!'
    >>> encrypted_message = tc.encrypt_message(message, pub_key)

### Computing Partial Decryptions

`t` share owners compute partial decryptions of a ciphertext using their shares:

    >>> partial_decryptions = []
    >>> for participant in [0, 2, 4]:
    ...     participant_share = key_shares[participant]
    ...     partial_decryption = tc.compute_partial_decryption(encrypted_message, participant_share)
    ...     partial_decryptions.append(partial_decryption)

### Combining Partial Decryptions

Combine these partial decryptions to recover the message:

    >>> decrypted_message = tc.decrypt_message(partial_decryptions, encrypted_message, thresh_params)
    >>> print(decrypted_message)
    Some secret message to be encrypted!

### Updating Ciphertexts

When the participants of the scheme change (adding participants, removing participants, ...) existing ciphertexts can be re-encrypted to be decryptable with the new shares.

First, create the new shares (for simplicity the centralized approach is shown here, in practice you want to use distributed key generation):

    >>> new_pub_key, new_key_shares = tc.create_public_key_and_shares_centralized(curve_params, thresh_params)

A third party computes non-secret values required for the generation of the re-encryption key for `max(t_old, t_new)` participants involved in the re-encryption key generation:

    >>> t_max = thresh_params.t
    >>> old_indices = [key_share.x for key_share in key_shares][:t_max]
    >>> new_indices = [key_share.x for key_share in new_key_shares][:t_max]

    >>> coefficients = []
    >>> for p in range(1, t_max + 1):
    ...     old_lc = tc.lagrange_coefficient_for_key_share_indices(old_indices, p, curve_params)
    ...     new_lc = tc.lagrange_coefficient_for_key_share_indices(new_indices, p, curve_params)
    ...     coefficients.append((old_lc, new_lc))

A number of `max(t_old, t_new)` participants now compute their partial re-encryption keys using these non-secret values and his shares:

    >>> partial_re_enc_keys = []
    >>> for p in range(t_max):
    ...     old_share = key_shares[p]
    ...     new_share = new_key_shares[p]
    ...     old_lc, new_lc = coefficients[p]
    ...     partial_re_enc_key = tc.compute_partial_re_encryption_key(old_share, old_lc, new_share, new_lc)
    ...     partial_re_enc_keys.append(partial_re_enc_key)

The third party computes the re-encryption key by combining the partial re-encryption keys:

    >>> re_enc_key = tc.combine_partial_re_encryption_keys(partial_re_enc_keys, pub_key, new_pub_key, thresh_params, thresh_params)

The encrypted message is re-encrypted to be decryptable by the new shares:

    >>> new_encrypted_message = tc.re_encrypt_message(encrypted_message, re_enc_key)

Decryption can now be performed using the new shares:

    >>> reconstruct_shares = [new_key_shares[i] for i in [0, 2, 4]]
    >>> partial_decryptions = [tc.compute_partial_decryption(new_encrypted_message, share) for share in reconstruct_shares]
    >>> decrypted_message = tc.decrypt_message(partial_decryptions, new_encrypted_message, thresh_params)
    >>> print(decrypted_message)
    Some secret message to be encrypted!
