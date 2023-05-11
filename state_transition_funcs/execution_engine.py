from config import *

from rlp import encode

from helper_funcs.misc import hash, hash_tree_root
# from helper_funcs.kzg_utils import blob_to_kzg, kzg_to_commitment, kzg_to_versioned_hash, verify_kzg_proof

from containers.beacon_block import BeaconBlockAndBlobs, BeaconBlock
# from containers import BlobTransactionNetworkWrapper
from containers.execution_payload import ExecutionPayload, ExecutionPayloadHeader, ExecutionPayloadWithoutBlockHash
from containers.transaction import SignedBlobTransaction



def notify_new_payload(execution_payload: ExecutionPayload) -> bool:
    """
    Return ``True`` if and only if ``execution_payload`` is valid with respect to ``self.execution_state``.
    """

    return True

    
# def validate_blob_transaction_wrapper(wrapper: BlobTransactionNetworkWrapper):
#     versioned_hashes = wrapper.tx.header.blob_versioned_hashes
#     kzgs = wrapper.blob_kzgs
#     blobs = wrapper.blobs
#     assert len(versioned_hashes) == len(kzgs) == len(blobs)
#     for versioned_hash, kzg, blob in zip(versioned_hashes, kzgs, blobs):
#         assert kzg == blob_to_kzg(blob)
#         assert versioned_hash == kzg_to_versioned_hash(kzg)


# def verify_blobs(block_and_blobs: BeaconBlockAndBlobs):
#     kzgs = block_and_blobs.block.message.body.blob_kzgs
#     blobs = block_and_blobs.blobs
#     assert len(kzgs) == len(blobs)
#     for kzg, blob in zip(kzgs, blobs):
#         assert blob_to_kzg(blob) == kzg
        


# def blob_verification_precompile(input: bytes) -> bytes:
#     # First 32 bytes = expected versioned hash
#     expected_v_hash = input[:32]
#     assert expected_v_hash[:1] == BLOB_COMMITMENT_VERSION_KZG
#     # Remaining bytes = list of little-endian data points
#     assert len(input) == 32 + 32 * CHUNKS_PER_BLOB
#     input_points = [
#         int.from_bytes(input[i:i+32], ENDIANNESS)
#         for i in range(32, len(input), 32)
#     ]
#     assert kzg_to_versioned_hash(blob_to_kzg(input_points)) == expected_v_hash
#     return bytes([])


# def point_evaluation_precompile(input: bytes) -> bytes:
#     # Verify P(z) = a
#     # versioned hash: first 32 bytes
#     versioned_hash = input[:32]
#     # Evaluation point: next 32 bytes
#     x = int.from_bytes(input[32:64], ENDIANNESS)
#     assert x < BLS_MODULUS
#     # Expected output: next 32 bytes
#     y = int.from_bytes(input[64:96], ENDIANNESS)
#     assert y < BLS_MODULUS
#     # The remaining data will always be the proof, including in future versions
#     # input kzg point: next 48 bytes
#     data_kzg = input[96:144]
#     assert kzg_to_versioned_hash(data_kzg) == versioned_hash
#     # Quotient kzg: next 48 bytes
#     quotient_kzg = input[144:192]
#     assert verify_kzg_proof(data_kzg, x, y, quotient_kzg)
#     return bytes([])


