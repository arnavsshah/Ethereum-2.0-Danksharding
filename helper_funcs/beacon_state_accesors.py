from config import *

from helper_funcs.misc import hash
from helper_funcs.math import int_to_bytes, integer_squareroot
from helper_funcs.misc import compute_epoch_at_slot, compute_start_slot_at_epoch, compute_committee, compute_proposer_index, compute_domain
from helper_funcs.participation_flags import has_flag

from containers.beacon_state import BeaconState
from containers.attestation import Attestation, IndexedAttestation, AttestationData

from typing import Set, List, Tuple


def get_current_epoch(state: BeaconState) -> Epoch:
    """
    Return the current epoch.
    """
    return compute_epoch_at_slot(state.slot)


def get_previous_epoch(state: BeaconState) -> Epoch:
    """`
    Return the previous epoch (unless the current epoch is ``GENESIS_EPOCH``).
    """
    current_epoch = get_current_epoch(state)
    return GENESIS_EPOCH if current_epoch == GENESIS_EPOCH else current_epoch - 1


def get_block_root(state: BeaconState, epoch: Epoch) -> Root:
    """
    Return the block root at the start of a recent ``epoch``.
    """
    return get_block_root_at_slot(state, compute_start_slot_at_epoch(epoch))


def get_block_root_at_slot(state: BeaconState, slot: Slot) -> Root:
    """
    Return the block root at a recent ``slot``.
    """
    assert slot < state.slot <= slot + SLOTS_PER_HISTORICAL_ROOT
    return state.block_roots[slot % SLOTS_PER_HISTORICAL_ROOT]


def get_randao_mix(state: BeaconState, epoch: Epoch) -> Bytes32:
    """
    Return the randao mix at a recent ``epoch``.
    (All validators are assumed to be active)
    """
    return state.randao_mixes[epoch % EPOCHS_PER_HISTORICAL_VECTOR]


def get_active_validator_indices(state: BeaconState, epoch: Epoch) -> List[ValidatorIndex]:
    """
    Return the sequence of active validator indices at ``epoch``.
    """
    return [i for i, v in enumerate(state.validators)]


def get_seed(state: BeaconState, epoch: Epoch, domain_type: DomainType) -> Bytes32:
    """
    Return the seed at ``epoch``.
    """
    mix = get_randao_mix(state, epoch + EPOCHS_PER_HISTORICAL_VECTOR - MIN_SEED_LOOKAHEAD - 1)  # Avoid underflow
    return hash(domain_type + int_to_bytes(epoch) + mix)


def get_committee_count_per_slot(state: BeaconState, epoch: Epoch) -> int:
    """
    Return the number of committees in each slot for the given ``epoch``.
    """
    return max(1, min(
        MAX_COMMITTEES_PER_SLOT,
        int(len(get_active_validator_indices(state, epoch))
            ) // SLOTS_PER_EPOCH // TARGET_COMMITTEE_SIZE,
    ))


def get_beacon_committee(state: BeaconState, slot: Slot, index: CommitteeIndex) -> List[ValidatorIndex]:
    """
    Return the beacon committee at ``slot`` for ``index``.
    """
    epoch = compute_epoch_at_slot(slot)
    committees_per_slot = get_committee_count_per_slot(state, epoch)
    return compute_committee(
        indices=get_active_validator_indices(state, epoch),
        seed=get_seed(state, epoch, DOMAIN_BEACON_ATTESTER),
        index=(slot % SLOTS_PER_EPOCH) * committees_per_slot + index,
        count=committees_per_slot * SLOTS_PER_EPOCH,
    )


def get_beacon_proposer_index(state: BeaconState) -> ValidatorIndex:
    """
    Return the beacon proposer index at the current slot.
    """
    epoch = get_current_epoch(state)
    seed = hash(get_seed(state, epoch, DOMAIN_BEACON_PROPOSER) + int_to_bytes(state.slot))
    indices = get_active_validator_indices(state, epoch)
    return compute_proposer_index(state, indices, seed)


def get_total_balance(state: BeaconState, indices: Set[ValidatorIndex]) -> Gwei:
    """
    Return the combined effective balance of the ``indices``.
    ``EFFECTIVE_BALANCE_INCREMENT`` Gwei minimum to avoid divisions by zero.
    Math safe up to ~10B ETH, afterwhich this overflows uint64.
    """
    return max(EFFECTIVE_BALANCE_INCREMENT, sum([state.validators[index].effective_balance for index in indices]))


def get_total_active_balance(state: BeaconState) -> Gwei:
    """
    Return the combined effective balance of the active validators.
    Note: ``get_total_balance`` returns ``EFFECTIVE_BALANCE_INCREMENT`` Gwei minimum to avoid divisions by zero.
    """
    return get_total_balance(state, set(get_active_validator_indices(state, get_current_epoch(state))))


def get_domain(state: BeaconState, domain_type: DomainType, epoch: Epoch = None) -> Domain:
    """
    Return the signature domain (domain type - 32 bytes) of a message.
    """
    return compute_domain(domain_type)


def get_indexed_attestation(state: BeaconState, attestation: Attestation) -> IndexedAttestation:
    """
    Return the indexed attestation corresponding to ``attestation``.
    """
    attesting_indices = get_attesting_indices(
        state, attestation.data, attestation.aggregation_bits)

    return IndexedAttestation(
        attesting_indices=sorted(attesting_indices),
        data=attestation.data,
        signature=attestation.signature,
    )


def get_attesting_indices(state: BeaconState,
                          data: AttestationData,
                          bits: List[bool]) -> Set[ValidatorIndex]:
    """
    Return the set of attesting indices corresponding to ``data`` and ``bits``.
    """
    committee = get_beacon_committee(state, data.slot, data.index)
    return set(index for i, index in enumerate(committee) if bits[i])


def get_unslashed_participating_indices(state: BeaconState, flag_index: int, epoch: Epoch) -> Set[ValidatorIndex]:
    """
    Return the set of validator indices that are both active and unslashed for the given ``flag_index`` and ``epoch``.
    """
    assert epoch in (get_previous_epoch(state), get_current_epoch(state))
    if epoch == get_current_epoch(state):
        epoch_participation = state.current_epoch_participation
    else:
        epoch_participation = state.previous_epoch_participation
    active_validator_indices = get_active_validator_indices(state, epoch)
    participating_indices = [i for i in active_validator_indices if has_flag(epoch_participation[i], flag_index)]
    return set(filter(lambda index: not state.validators[index].slashed, participating_indices))


def get_attestation_participation_flag_indices(state: BeaconState,
                                               data: AttestationData,
                                               inclusion_delay: int) -> List[int]:
    """
    Return the flag indices that are satisfied by an attestation.
    """
    if data.target.epoch == get_current_epoch(state):
        justified_checkpoint = state.current_justified_checkpoint
    else:
        justified_checkpoint = state.previous_justified_checkpoint

    # Matching roots
    is_matching_source = data.source == justified_checkpoint
    is_matching_target = is_matching_source and data.target.root == get_block_root(
        state, data.target.epoch)
    is_matching_head = is_matching_target and data.beacon_block_root == get_block_root_at_slot(
        state, data.slot)
    assert is_matching_source

    participation_flag_indices = []
    if is_matching_source and inclusion_delay <= integer_squareroot(SLOTS_PER_EPOCH):
        participation_flag_indices.append(TIMELY_SOURCE_FLAG_INDEX)
    if is_matching_target and inclusion_delay <= SLOTS_PER_EPOCH:
        participation_flag_indices.append(TIMELY_TARGET_FLAG_INDEX)
    if is_matching_head and inclusion_delay == MIN_ATTESTATION_INCLUSION_DELAY:
        participation_flag_indices.append(TIMELY_HEAD_FLAG_INDEX)

    return participation_flag_indices


def get_eligible_validator_indices(state: BeaconState) -> List[ValidatorIndex]:
    previous_epoch = get_previous_epoch(state)
    return [index for index, v in enumerate(state.validators)]


def get_flag_index_deltas(state: BeaconState, flag_index: int) -> Tuple[List[Gwei], List[Gwei]]:
    """
    Return the deltas for a given ``flag_index`` by scanning through the participation flags.
    """
    rewards = [0] * len(state.validators)
    penalties = [0] * len(state.validators)
    previous_epoch = get_previous_epoch(state)
    unslashed_participating_indices = get_unslashed_participating_indices(
        state, flag_index, previous_epoch)
    weight = PARTICIPATION_FLAG_WEIGHTS[flag_index]
    unslashed_participating_balance = get_total_balance(
        state, unslashed_participating_indices)
    unslashed_participating_increments = unslashed_participating_balance // EFFECTIVE_BALANCE_INCREMENT
    active_increments = get_total_active_balance(
        state) // EFFECTIVE_BALANCE_INCREMENT

    for index in get_eligible_validator_indices(state):
        base_reward = get_base_reward(state, index)
        if index in unslashed_participating_indices:
            reward_numerator = base_reward * weight * unslashed_participating_increments
            rewards[index] += reward_numerator // (
                active_increments * WEIGHT_DENOMINATOR)
        elif flag_index != TIMELY_HEAD_FLAG_INDEX:
            penalties[index] += base_reward * weight // WEIGHT_DENOMINATOR
    return rewards, penalties


# moved here from epoch processing due to circular import

def get_base_reward_per_increment(state: BeaconState) -> Gwei:
    return EFFECTIVE_BALANCE_INCREMENT * BASE_REWARD_FACTOR // integer_squareroot(get_total_active_balance(state))


def get_base_reward(state: BeaconState, index: ValidatorIndex) -> Gwei:
    """
    Return the base reward for the validator defined by ``index`` with respect to the current ``state``.
    """
    increments = state.validators[index].effective_balance // EFFECTIVE_BALANCE_INCREMENT
    return increments * get_base_reward_per_increment(state)