from config import *

from rlp import encode

from helper_funcs.misc import hash, hash_tree_root

from containers.beacon_block import BeaconBlock, BeaconBlockHeader, BeaconBlockBody, ProposerSlashing, AttesterSlashing, SignedBeaconBlock
from containers.attestation import Attestation
from containers.execution_payload import ExecutionPayload, ExecutionPayloadHeader, ExecutionPayloadWithoutBlockHash
from containers.transaction import SignedBlobTransaction


from typing import List

def build_beacon_block_body(randao_reveal: BLSSignature, 
                        proposer_slashings: List[ProposerSlashing], attester_slashings: List[AttesterSlashing],
                        attestations: List[Attestation], execution_payload: ExecutionPayload) -> BeaconBlockBody:
    
    return BeaconBlockBody(randao_reveal=randao_reveal,
                        proposer_slashings=proposer_slashings,
                        attester_slashings=attester_slashings,
                        attestations=attestations,
                        execution_payload=execution_payload)



def build_beacon_block(slot: Slot, proposer_index:ValidatorIndex, parent_root: Root, 
                    state_root: Root, body: BeaconBlockBody) -> BeaconBlock:
    
    return BeaconBlock(slot=slot,
                    proposer_index=proposer_index,
                    parent_root=parent_root,
                    state_root=state_root,
                    body=body)



def build_beacon_block_header(beacon_block: BeaconBlock) -> BeaconBlockHeader:

    body_root = hash_tree_root(beacon_block.body)

    return BeaconBlockHeader(slot=beacon_block.slot,
                            proposer_index=beacon_block.proposer_index,
                            parent_root=beacon_block.parent_root,
                            state_root=beacon_block.state_root,
                            body_root=body_root)

def build_signed_beacon_block(message: BeaconBlock, signature: BLSSignature) -> SignedBeaconBlock:
    return SignedBeaconBlock(message=message, signature=signature)