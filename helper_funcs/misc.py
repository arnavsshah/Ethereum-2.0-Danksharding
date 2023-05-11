from hashlib import sha256
import rlp
from rlp import Serializable, encode

from config import *
from helper_funcs.math import *
from containers.beacon_state import BeaconState
from containers.signing_data import SigningData

from typing import List


def hash(data: bytes) -> Bytes32:
    return sha256(data).digest()


# TODO make more general rlp.sedes.serializable.SerializableBase
def hash_tree_root(object: Serializable) -> Root:
    if 'rlp' in str(type(object)) or 'containers' in str(type(object)):
        sedes = type(object)
    else:
        sedes = None
    data = encode(object, sedes)
    return sha256(data).digest()


def compute_shuffled_index(index: int, index_count: int, seed: Bytes32) -> int:
    """
    Return the shuffled index corresponding to ``seed`` (and ``index_count``).
    """
    assert index < index_count

    # Swap or not (https://link.springer.com/content/pdf/10.1007%2F978-3-642-32009-5_1.pdf)
    # See the 'generalized domain' algorithm on page 3
    for current_round in range(SHUFFLE_ROUND_COUNT):
        pivot = bytes_to_int(
            hash(seed + int_to_bytes(int(current_round)))[0:8]) % index_count
        flip = (pivot + index_count - index) % index_count
        position = max(index, flip)
        source = hash(
            seed
            + int_to_bytes(int(current_round))
            + int_to_bytes(int(position // 256))
        )
        byte = int(source[(position % 256) // 8])
        bit = (byte >> (position % 8)) % 2
        index = flip if bit else index

    return index


def compute_proposer_index(state: BeaconState, indices: List[ValidatorIndex], seed: Bytes32) -> ValidatorIndex:
    """
    Return from ``indices`` a random index sampled by effective balance.
    """
    assert len(indices) > 0
    MAX_RANDOM_BYTE = 2**8 - 1
    i = int(0)
    total = int(len(indices))
    while True:
        candidate_index = indices[compute_shuffled_index(
            i % total, total, seed)]
        random_byte = hash(seed + int_to_bytes(int(i // 32)))[i % 32]
        effective_balance = state.validators[candidate_index].effective_balance
        if effective_balance * MAX_RANDOM_BYTE >= MAX_EFFECTIVE_BALANCE * random_byte:
            return candidate_index
        i += 1


def compute_committee(indices: List[ValidatorIndex],
                      seed: Bytes32,
                      index: int,
                      count: int) -> List[ValidatorIndex]:
    """
    Return the committee corresponding to ``indices``, ``seed``, ``index``, and committee ``count``.
    """
    start = (len(indices) * index) // count
    end = (len(indices) * int(index + 1)) // count
    return [indices[compute_shuffled_index(int(i), int(len(indices)), seed)] for i in range(start, end)]


def compute_epoch_at_slot(slot: Slot) -> Epoch:
    """
    Return the epoch number at ``slot``.
    """
    return slot // SLOTS_PER_EPOCH


def compute_start_slot_at_epoch(epoch: Epoch) -> Slot:
    """
    Return the start slot of ``epoch``.
    """
    return epoch * SLOTS_PER_EPOCH


def compute_domain(domain_type: DomainType) -> Domain:
    """
    Return the domain for the ``domain_type``. Fork version and genesis validators root removed
    """

    return bytes(domain_type + b'\x00' * 28)  # Bytes32


def compute_signing_root(ssz_object: Serializable, domain: Domain) -> Root:
    """
    Return the signing root for the corresponding signing data.
    """
    return hash_tree_root(SigningData(object_root=hash_tree_root(ssz_object), domain=domain))


def compute_timestamp_at_slot(state: BeaconState, slot: Slot) -> int:
    slots_since_genesis = slot - GENESIS_SLOT
    return int(state.genesis_time + slots_since_genesis * SECONDS_PER_SLOT)
