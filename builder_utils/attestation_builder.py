from config import *

from containers.checkpoint import Checkpoint
from containers.attestation import AttestationData, Attestation, AggregateAndProof, SignedAggregateAndProof

from typing import List

def build_attestation_data(slot: Slot, index: CommitteeIndex, beacon_block_root: Root, 
                        source: Checkpoint, target: Checkpoint) -> AttestationData:
    
    return AttestationData(slot=slot, 
                        index=index,
                        beacon_block_root=beacon_block_root,
                        source=source,
                        target=target)


def build_attestation(aggregation_bits: List[bool], data: AttestationData, signature: BLSSignature) -> Attestation:
    
    return Attestation(aggregation_bits=aggregation_bits, 
                    data=data,
                    signature=signature)


def build_aggregate_and_proof(aggregator_index: ValidatorIndex, aggregate: Attestation, selection_proof: BLSSignature) -> AggregateAndProof:

    return AggregateAndProof(aggregator_index=aggregator_index,
                            aggregate=aggregate,
                            selection_proof=selection_proof) 


def build_signed_aggregate_and_proof(message: AggregateAndProof, signature: BLSSignature) -> SignedAggregateAndProof:

    return SignedAggregateAndProof(message=message, signature=signature) 