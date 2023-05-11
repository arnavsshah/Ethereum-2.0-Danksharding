from config import *

from helper_funcs.misc import hash_tree_root, compute_signing_root
import helper_funcs.bls_utils as bls
from helper_funcs.beacon_state_accesors import get_domain

from state_transition_funcs.block_processing import process_block
from state_transition_funcs.epoch_processing import process_epoch

from containers.beacon_state import BeaconState
from containers.beacon_block import SignedBeaconBlock, BeaconBlockHeader

from typing import List

from rlp import encode, decode


def state_transition(state: BeaconState, signed_block: SignedBeaconBlock, validate_result: bool=True) -> None:
    block = signed_block.message
    # Process slots (including those with no blocks) since block
    process_slots(state, block.slot)
    # Verify signature
    if validate_result:
        assert verify_block_signature(state, signed_block), f'signature incorrect for block in slot {block.slot}, proposer index {block.proposer_index}'
    # Process block
    process_block(state, block)
    # Verify state root
    if validate_result:
        assert block.state_root == hash_tree_root(state), f'state root incorrect for block in slot {block.slot}, proposer index {block.proposer_index}'


def verify_block_signature(state: BeaconState, signed_block: SignedBeaconBlock) -> bool:
    proposer = state.validators[signed_block.message.proposer_index]
    signing_root = compute_signing_root(signed_block.message, get_domain(DOMAIN_BEACON_PROPOSER))
    return bls.Verify(proposer.pubkey, signing_root, signed_block.signature)


def process_slots(state: BeaconState, slot: Slot) -> None:
    assert state.slot < slot
    while state.slot < slot:
        process_slot(state)
        # Process epoch on the start slot of the next epoch
        if (state.slot + 1) % SLOTS_PER_EPOCH == 0:
            process_epoch(state)
        state.slot = state.slot + 1

    
def process_slot(state: BeaconState) -> None:
    # Cache state root
    previous_state_root = hash_tree_root(state)
    state_roots = list(state.state_roots)
    state_roots[state.slot % SLOTS_PER_HISTORICAL_ROOT] = previous_state_root
    state.state_roots = tuple(state_roots)
    
    # Cache latest block header state root
    if state.latest_block_header.state_root == b'stub':  # set in process_block_header()
        state.latest_block_header.state_root = previous_state_root

    # Cache block root
    previous_block_root = hash_tree_root(state.latest_block_header)
    block_roots = list(state.block_roots)
    block_roots[state.slot % SLOTS_PER_HISTORICAL_ROOT] = previous_block_root
    state.block_root = tuple(block_roots)