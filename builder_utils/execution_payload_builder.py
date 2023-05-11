from config import *

from rlp import encode

from helper_funcs.misc import hash_tree_root

from containers.execution_payload import ExecutionPayload, ExecutionPayloadHeader, ExecutionPayloadWithoutBlockHash
from containers.transaction import SignedBlobTransaction

from typing import List

def build_execution_payload(parent_hash=Hash32, fee_recipient=ExecutionAddress, state_root=Bytes32,
                            prev_randao=Bytes32, gas_limit=int,
                            gas_used=int, timestamp=int, base_fee_per_gas=int,
                            blob_transactions=List[SignedBlobTransaction]) -> ExecutionPayload:
    

    temp = ExecutionPayloadWithoutBlockHash(parent_hash=parent_hash,
                                            fee_recipient=fee_recipient,
                                            state_root=state_root,
                                            prev_randao=prev_randao,
                                            gas_limit=gas_limit,
                                            gas_used=gas_used,
                                            timestamp=timestamp,
                                            base_fee_per_gas=base_fee_per_gas,
                                            blob_transactions=blob_transactions)
    
    block_hash = hash_tree_root(temp)

    return ExecutionPayload(parent_hash=parent_hash,
                            fee_recipient=fee_recipient,
                            state_root=state_root,
                            prev_randao=prev_randao,
                            gas_limit=gas_limit,
                            gas_used=gas_used,
                            timestamp=timestamp,
                            base_fee_per_gas=base_fee_per_gas,
                            block_hash=block_hash,
                            blob_transactions=blob_transactions)



def build_execution_payload_header(execution_payload: ExecutionPayload) -> ExecutionPayloadHeader:
    
    if len(execution_payload.blob_transactions) > 0:
        blob_transactions_root = hash_tree_root(execution_payload.blob_transactions[0])
    
    else:
        blob_transactions_root = b''

    return ExecutionPayloadHeader(parent_hash=execution_payload.parent_hash,
                                fee_recipient=execution_payload.fee_recipient,
                                state_root=execution_payload.state_root,
                                prev_randao=execution_payload.prev_randao,
                                gas_limit=execution_payload.gas_limit,
                                gas_used=execution_payload.gas_used,
                                timestamp=execution_payload.timestamp,
                                base_fee_per_gas=execution_payload.base_fee_per_gas,
                                block_hash=execution_payload.block_hash,
                                blob_transactions_root=blob_transactions_root)