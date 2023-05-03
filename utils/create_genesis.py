from config import *

import pickle

from helper_funcs.misc import hash_tree_root

from builder_utils.execution_payload_builder import build_execution_payload, build_execution_payload_header
from builder_utils.beacon_block_builder import build_beacon_block_body, build_beacon_block, build_beacon_block_header
from builder_utils.checkpoint_builder import build_checkpoint
from builder_utils.validator_builder import build_validator

from containers.beacon_block import BeaconBlock, BeaconBlockHeader, BeaconBlockBody
from containers.beacon_state import BeaconState
from containers.checkpoint import Checkpoint
from containers.execution_payload import ExecutionPayload, ExecutionPayloadHeader
from containers.validator import Validator

from typing import List


# --------------------------------Execution Payload-------------------------------------

def get_genesis_execution_payload() -> ExecutionPayload:

    parent_hash = b'stub'
    fee_recipient = b'stub'
    state_root = b'stub'
    prev_randao = b'stub'
    gas_limit = 0
    gas_used = 0
    timestamp = GENESIS_TIME
    base_fee_per_gas = 0
    blob_transactions = []

    genesis_execution_payload = build_execution_payload(parent_hash=parent_hash,
                                                    fee_recipient=fee_recipient,
                                                    state_root=state_root,
                                                    prev_randao=prev_randao,
                                                    gas_limit=gas_limit,
                                                    gas_used=gas_used,
                                                    timestamp=timestamp,
                                                    base_fee_per_gas=base_fee_per_gas,
                                                    blob_transactions=blob_transactions)

    return genesis_execution_payload



def get_genesis_execution_payload_header(genesis_execution_payload: ExecutionPayload) -> ExecutionPayloadHeader:
    return build_execution_payload_header(genesis_execution_payload)

# --------------------------------Execution Payload-------------------------------------




# --------------------------------Beacon Block-------------------------------------

def get_genesis_beacon_block_body(genesis_execution_payload: ExecutionPayload) -> BeaconBlockBody:
    randao_reveal = b'stub'
    proposer_slashings = []
    attester_slashings = []
    attestations = []
    execution_payload = genesis_execution_payload

    genesis_beacon_block_body = build_beacon_block_body(randao_reveal=randao_reveal,
                                                    proposer_slashings=proposer_slashings,
                                                    attester_slashings=attester_slashings,
                                                    attestations=attestations,
                                                    execution_payload=execution_payload)
    
    return genesis_beacon_block_body


def get_genesis_beacon_block(genesis_beacon_block_body: BeaconBlockBody) -> BeaconBlock:
    slot = 0
    proposer_index = 0
    parent_root = b'stub'
    state_root = b'stub'
    body = genesis_beacon_block_body

    genesis_beacon_block = build_beacon_block(slot=slot,
                                            proposer_index=proposer_index,
                                            parent_root=parent_root,
                                            state_root=state_root,
                                            body=body)

    return genesis_beacon_block


def get_genesis_beacon_block_header(genesis_beacon_block: BeaconBlock) -> BeaconBlockHeader:
    return build_beacon_block_header(genesis_beacon_block)

# --------------------------------Beacon Block-------------------------------------




# --------------------------------Checkpoint-------------------------------------

def get_genesis_checkpoint(root: Root) -> Checkpoint:
    return build_checkpoint(epoch=0, root=root)

# --------------------------------Checkpoint-------------------------------------




# --------------------------------Beacon State-------------------------------------

def get_genesis_state(genesis_beacon_block_header: BeaconBlockHeader, 
                    validators: List[Validator], genesis_checkpoint: Checkpoint, 
                    genesis_execution_payload_header: ExecutionPayloadHeader) -> BeaconState:
    
    seed_randomness = b'stub'

    genesis_state = BeaconState(genesis_time=GENESIS_TIME,
                                genesis_validators_root=GENESIS_VALIDATORS_ROOT,
                                slot=0,
                                latest_block_header=genesis_beacon_block_header,
                                block_roots=[],
                                state_roots=[],
                                validators=validators,
                                balances=[32 for _ in validators],
                                randao_mixes=[seed_randomness] * EPOCHS_PER_HISTORICAL_VECTOR,
                                slashings=[],
                                previous_epoch_participation=[],
                                current_epoch_participation=[],
                                justification_bits=[],
                                previous_justified_checkpoint=genesis_checkpoint,
                                current_justified_checkpoint=genesis_checkpoint,
                                finalized_checkpoint=genesis_checkpoint,
                                latest_execution_payload_header=genesis_execution_payload_header
                                )


    return genesis_state

# --------------------------------Beacon State-------------------------------------


def create_genesis():
    bls_public_keys_file = 'data/bls_public_keys.pkl'

    with open(bls_public_keys_file, 'rb') as f:
        validator_bls_public_keys = pickle.load(f)

    # validators
    validators = [build_validator(pubkey=pubkey, effective_balance=32, slashed=False) for pubkey in validator_bls_public_keys]

    # execution payload
    genesis_execution_payload = get_genesis_execution_payload()
    genesis_execution_payload_header = get_genesis_execution_payload_header(genesis_execution_payload=genesis_execution_payload)

    # beacon block
    genesis_beacon_block_body = get_genesis_beacon_block_body(genesis_execution_payload=genesis_execution_payload)
    genesis_beacon_block = get_genesis_beacon_block(genesis_beacon_block_body=genesis_beacon_block_body)
    genesis_beacon_block_header = get_genesis_beacon_block_header(genesis_beacon_block=genesis_beacon_block)

    # checkpoint
    # genesis_checkpoint = get_genesis_checkpoint(genesis_block_root=hash_tree_root(genesis_beacon_block))
    genesis_checkpoint = get_genesis_checkpoint(genesis_block_root=b'stub')

    # beacon state
    genesis_beacon_state = get_genesis_state(genesis_beacon_block_header=genesis_beacon_block_header,
                                            validators=validators,
                                            genesis_checkpoint=genesis_checkpoint,
                                            genesis_execution_payload_header=genesis_execution_payload_header)


    return genesis_beacon_block, genesis_beacon_state