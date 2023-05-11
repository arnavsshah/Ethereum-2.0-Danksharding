from rlp import Serializable
from rlp.sedes import big_endian_int, CountableList

from config import *
from containers.transaction import SignedBlobTransaction

class ExecutionPayload(Serializable):
    '''
    Replaces Eth1 blocks. Represents all transactions in a block 
    and resides in the BeaconBlock
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        # Execution block header fields
        ('parent_hash', Hash32()),
        ('fee_recipient', ExecutionAddress()),  # 'beneficiary' in the yellow paper
        ('state_root', Bytes32()),
        ('prev_randao', Bytes32()),  # 'difficulty' in the yellow paper
        ('gas_limit', big_endian_int),
        ('gas_used', big_endian_int),
        ('timestamp', big_endian_int),
        ('base_fee_per_gas', big_endian_int),

        # Extra payload fields
        ('block_hash', Hash32()),  # Hash of execution block
        # TODO - check max len 
        ('blob_transactions', CountableList(SignedBlobTransaction, max_length=MAX_TRANSACTIONS_PER_PAYLOAD))
    )



class ExecutionPayloadWithoutBlockHash(Serializable):
    '''
    Used to calculate the block hash easily (hacky way!)
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        # Execution block header fields
        ('parent_hash', Hash32()),
        ('fee_recipient', ExecutionAddress()),  # 'beneficiary' in the yellow paper
        ('state_root', Bytes32()),
        ('prev_randao', Bytes32()),  # 'difficulty' in the yellow paper
        ('gas_limit', big_endian_int),
        ('gas_used', big_endian_int),
        ('timestamp', big_endian_int),
        ('base_fee_per_gas', big_endian_int),

        # Extra payload fields
        ('blob_transactions', CountableList(SignedBlobTransaction, max_length=MAX_TRANSACTIONS_PER_PAYLOAD))
    )




class ExecutionPayloadHeader(Serializable):
    '''
    Replaces Eth1 block headers. Represents the hash of all transactions in a block 
    and the latest header resides in the BeaconState
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        # Execution block header fields
        ('parent_hash', Hash32()),
        ('fee_recipient', ExecutionAddress()),
        ('state_root', Bytes32()),
        ('prev_randao', Bytes32()),
        ('gas_limit', big_endian_int),
        ('gas_used', big_endian_int),
        ('timestamp', big_endian_int),
        ('base_fee_per_gas', big_endian_int),

        # Extra payload fields
        ('block_hash', Hash32()),  # Hash of execution block
        ('blob_transactions_root', Root())
    )