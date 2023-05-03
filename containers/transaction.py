from rlp import Serializable
from rlp.sedes import big_endian_int, List, CountableList

from config import *


class BlobTransaction(Serializable):
    '''
    Transaction format for "blob-carrying transactions" which contain a large amount of data 
    that cannot be accessed by EVM execution, but whose commitment can be accessed. 
    The format is intended to be fully compatible with the format that will be used in full sharding.
    '''
    
    Serializable._in_mutable_context = True
    
    fields = (
        ('nonce', big_endian_int),
        ('max_fee_per_gas', big_endian_int),
        ('gas_limit', big_endian_int),
        ('sender', ExecutionAddress()),
        ('receiver', ExecutionAddress()),
        ('value', big_endian_int),
        # ('blob_versioned_hashes', CountableList(VersionedHash, max_length=MAX_BLOBS_PER_TX))
    )


class SignedBlobTransaction(Serializable):
    '''
    Signed blob-carrying transaction which will be included in a shard blob as part of a beacon block
    '''
    
    Serializable._in_mutable_context = True
    
    fields = (
        ('message', BlobTransaction),
        ('signature', ECDSASignature())  # ECDSASignature should ideally be split into v, r, s fields but we do not check the validity of blob transactions at the moment, so it does not matter.
    )


class BlobTransactionNetworkWrapper(Serializable):
    '''
    Transactions are passed around the network in this format. Consists of the signed transaction, blobs, and the KZG commitments
    '''
    
    Serializable._in_mutable_context = True
    
    fields = (
        ('tx', SignedBlobTransaction),
        # ('blob_kzgs', CountableList(KZGCommitment, max_length=MAX_BLOBS_PER_TX)),
        # ('blobs', List([BLSFieldElement for _ in range(CHUNKS_PER_BLOB)]))
    )
