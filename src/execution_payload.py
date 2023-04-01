from typing import List

from config.custom_constants import *
from config.custom_presets import *
from config.custom_types import *


class ExecutionPayload():
    '''
    Replaces Eth1 blocks. Represents all transactions in a block 
    and resides in the BeaconBlock
    '''
    # Execution block header fields
    parent_hash: Hash32
    fee_recipient: ExecutionAddress  # 'beneficiary' in the yellow paper
    state_root: Bytes32
    prev_randao: Bytes32  # 'difficulty' in the yellow paper
    block_number: int  # 'number' in the yellow paper
    gas_limit: int
    gas_used: int
    timestamp: int
    base_fee_per_gas: int

    # Extra payload fields
    block_hash: Hash32  # Hash of execution block
    transactions: List[Transaction, MAX_TRANSACTIONS_PER_PAYLOAD]


class ExecutionPayloadHeader():
    '''
    Replaces Eth1 block headers. Represents the hash of all transactions in a block 
    and the latest header resides in the BeaconState
    '''
    # Execution block header fields
    parent_hash: Hash32
    fee_recipient: ExecutionAddress
    state_root: Bytes32
    prev_randao: Bytes32
    block_number: int
    gas_limit: int
    gas_used: int
    timestamp: int
    base_fee_per_gas: int

    # Extra payload fields
    block_hash: Hash32  # Hash of execution block
    transactions_root: Root