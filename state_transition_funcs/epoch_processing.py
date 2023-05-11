from config import *

from helper_funcs.math import integer_squareroot
from helper_funcs.misc import hash_tree_root
from helper_funcs.beacon_state_accesors import get_randao_mix, get_current_epoch, get_unslashed_participating_indices, get_total_active_balance, get_total_balance, get_previous_epoch, get_block_root, get_flag_index_deltas
from helper_funcs.beacon_state_mutators import increase_balance, decrease_balance

from containers.beacon_state import BeaconState
from containers.checkpoint import Checkpoint

from typing import List


def process_epoch(state: BeaconState) -> None:
    process_justification_and_finalization(state)  # [Modified in Altair]
    process_rewards_and_penalties(state)  # [Modified in Altair]
    process_slashings(state)  # [Modified in Altair]
    process_effective_balance_updates(state)
    process_slashings_reset(state)
    process_randao_mixes_reset(state)
    process_participation_flag_updates(state)  # [New in Altair]



def process_justification_and_finalization(state: BeaconState) -> None:
    # Initial FFG checkpoint values have a `0x00` stub for `root`.
    # Skip FFG updates in the first two epochs to avoid corner cases that might result in modifying this stub.
    if get_current_epoch(state) <= GENESIS_EPOCH + 1:
        return
    previous_indices = get_unslashed_participating_indices(state, TIMELY_TARGET_FLAG_INDEX, get_previous_epoch(state))
    current_indices = get_unslashed_participating_indices(state, TIMELY_TARGET_FLAG_INDEX, get_current_epoch(state))
    total_active_balance = get_total_active_balance(state)
    previous_target_balance = get_total_balance(state, previous_indices)
    current_target_balance = get_total_balance(state, current_indices)
    weigh_justification_and_finalization(state, total_active_balance, previous_target_balance, current_target_balance)




def weigh_justification_and_finalization(state: BeaconState,
                                         total_active_balance: Gwei,
                                         previous_epoch_target_balance: Gwei,
                                         current_epoch_target_balance: Gwei) -> None:
    previous_epoch = get_previous_epoch(state)
    current_epoch = get_current_epoch(state)
    old_previous_justified_checkpoint = state.previous_justified_checkpoint
    old_current_justified_checkpoint = state.current_justified_checkpoint

    # Process justifications
    state.previous_justified_checkpoint = state.current_justified_checkpoint

    justification_bits = list(state.justification_bits)
    justification_bits[1:] = justification_bits[:JUSTIFICATION_BITS_LENGTH - 1]
    justification_bits[0] = 0  # 0b0 -> 0
    if previous_epoch_target_balance * 3 >= total_active_balance * 2:
        state.current_justified_checkpoint = Checkpoint(epoch=previous_epoch,
                                                        root=get_block_root(state, previous_epoch))
        justification_bits[1] = 1  # 0b1 -> 1
    if current_epoch_target_balance * 3 >= total_active_balance * 2:
        state.current_justified_checkpoint = Checkpoint(epoch=current_epoch,
                                                        root=get_block_root(state, current_epoch))
        justification_bits[0] = 1  # 0b1 -> 1

    state.justification_bits = tuple(justification_bits)

    # Process finalizations
    bits = state.justification_bits
    # The 2nd/3rd/4th most recent epochs are justified, the 2nd using the 4th as source
    if all(bits[1:4]) and old_previous_justified_checkpoint.epoch + 3 == current_epoch:
        state.finalized_checkpoint = old_previous_justified_checkpoint
    # The 2nd/3rd most recent epochs are justified, the 2nd using the 3rd as source
    if all(bits[1:3]) and old_previous_justified_checkpoint.epoch + 2 == current_epoch:
        state.finalized_checkpoint = old_previous_justified_checkpoint
    # The 1st/2nd/3rd most recent epochs are justified, the 1st using the 3rd as source
    if all(bits[0:3]) and old_current_justified_checkpoint.epoch + 2 == current_epoch:
        state.finalized_checkpoint = old_current_justified_checkpoint
    # The 1st/2nd most recent epochs are justified, the 1st using the 2nd as source
    if all(bits[0:2]) and old_current_justified_checkpoint.epoch + 1 == current_epoch:
        state.finalized_checkpoint = old_current_justified_checkpoint


def get_finality_delay(state: BeaconState) -> int:
    return get_previous_epoch(state) - state.finalized_checkpoint.epoch


def process_rewards_and_penalties(state: BeaconState) -> None:
    # No rewards are applied at the end of `GENESIS_EPOCH` because rewards are for work done in the previous epoch
    if get_current_epoch(state) == GENESIS_EPOCH:
        return

    flag_deltas = [get_flag_index_deltas(state, flag_index) for flag_index in range(len(PARTICIPATION_FLAG_WEIGHTS))]
    deltas = flag_deltas
    for (rewards, penalties) in deltas:
        for index in range(len(state.validators)):
            increase_balance(state, index, rewards[index])
            decrease_balance(state, index, penalties[index])


def process_slashings(state: BeaconState) -> None:
    epoch = get_current_epoch(state)
    total_balance = get_total_active_balance(state)
    adjusted_total_slashing_balance = min(
        sum(state.slashings) * PROPORTIONAL_SLASHING_MULTIPLIER_BELLATRIX,
        total_balance
    )
    for index, validator in enumerate(state.validators):
        if validator.slashed and epoch + EPOCHS_PER_SLASHINGS_VECTOR // 2 == validator.withdrawable_epoch:
            increment = EFFECTIVE_BALANCE_INCREMENT  # Factored out from penalty numerator to avoid uint64 overflow
            penalty_numerator = validator.effective_balance // increment * adjusted_total_slashing_balance
            penalty = penalty_numerator // total_balance * increment
            decrease_balance(state, ValidatorIndex(index), penalty)


def process_effective_balance_updates(state: BeaconState) -> None:
    # Update effective balances with hysteresis
    for index, validator in enumerate(state.validators):
        balance = state.balances[index]
        HYSTERESIS_INCREMENT = int(EFFECTIVE_BALANCE_INCREMENT // HYSTERESIS_QUOTIENT)
        DOWNWARD_THRESHOLD = HYSTERESIS_INCREMENT * HYSTERESIS_DOWNWARD_MULTIPLIER
        UPWARD_THRESHOLD = HYSTERESIS_INCREMENT * HYSTERESIS_UPWARD_MULTIPLIER
        if (
            balance + DOWNWARD_THRESHOLD < validator.effective_balance
            or validator.effective_balance + UPWARD_THRESHOLD < balance
        ):
            validator.effective_balance = min(balance - balance % EFFECTIVE_BALANCE_INCREMENT, MAX_EFFECTIVE_BALANCE)



def process_slashings_reset(state: BeaconState) -> None:
    next_epoch = get_current_epoch(state) + 1
    # Reset slashings
    slashings = list(state.slashings)
    slashings[next_epoch % EPOCHS_PER_SLASHINGS_VECTOR] = 0
    state.slashings = tuple(slashings)


def process_randao_mixes_reset(state: BeaconState) -> None:
    current_epoch = get_current_epoch(state)
    next_epoch = current_epoch + 1
    # Set randao mix
    randao_mixes = list(state.randao_mixes)
    randao_mixes[next_epoch % EPOCHS_PER_HISTORICAL_VECTOR] = get_randao_mix(state, current_epoch)
    state.randao_mixes = tuple(randao_mixes)

def process_participation_flag_updates(state: BeaconState) -> None:
    state.previous_epoch_participation = state.current_epoch_participation
    state.current_epoch_participation = tuple([0 for _ in range(len(state.validators))])





