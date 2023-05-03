from rlp import Serializable
from rlp.sedes import List, CountableList

from config import *
from containers.attestation import Attestation, IndexedAttestation
from containers.execution_payload import ExecutionPayload


class BeaconBlockHeader(Serializable):
    '''
    Used in the BeaconState
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        ('slot', Slot()),
        ('proposer_index', ValidatorIndex()),
        ('parent_root', Root()),
        ('state_root', Root()),
        ('body_root', Root()),
    )

class SignedBeaconBlockHeader(Serializable):
    '''
    Used for slashing
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        ('message', BeaconBlockHeader),
        ('signature', BLSSignature())
    )

class ProposerSlashing(Serializable):
    '''
    ProposerSlashings may be included in blocks to prove that a validator 
    has broken the rules and ought to be slashed. 
    Proposers receive a reward for correctly submitting these.
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        ('signed_header_1', SignedBeaconBlockHeader),
        ('signed_header_2', SignedBeaconBlockHeader)
    )


class AttesterSlashing(Serializable):
    '''
    AttesterSlashings may be included in blocks to prove that one or more validators 
    in a committee has broken the rules and ought to be slashed. 
    Proposers receive a reward for correctly submitting these.
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        ('attestation_1', IndexedAttestation),
        ('attestation_2', IndexedAttestation)
    )


class BeaconBlockBody(Serializable):
    '''
    BeaconBlockBody resides in a BeaconBlock.
    '''

    Serializable._in_mutable_context = True
        
    fields = (
        ('randao_reveal', BLSSignature()),

        # Operations
        ('proposer_slashings', CountableList(ProposerSlashing, max_length=MAX_PROPOSER_SLASHINGS)),
        ('attester_slashings', CountableList(AttesterSlashing, max_length=MAX_ATTESTER_SLASHINGS)),
        ('attestations', CountableList(Attestation, max_length=MAX_ATTESTATIONS)),

        # Execution
        ('execution_payload', ExecutionPayload),

        # KZG commitments
        # ('blob_kzg_commitments', CountableList(KZGCommitment, max_length=MAX_BLOBS_PER_BLOCK))
    )


class BeaconBlock(Serializable):
    '''
    BeaconBlock is used to communicate network updates to all the other validators, 
    and those validators update their own BeaconState by applying BeaconBlocks.
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        ('slot', Slot()),
        ('proposer_index', ValidatorIndex()),
        ('parent_root', Root()),
        ('state_root', Root()),
        ('body', BeaconBlockBody),
    )


class SignedBeaconBlock(Serializable):
    '''
    Used for slashing
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        ('message', BeaconBlock),
        ('signature', BLSSignature())
    )


class BeaconBlockAndBlobs(Serializable):
    '''
    Nodes broadcast this over the network instead of plain beacon blocks
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        ('block',SignedBeaconBlock),
        ('blobs', CountableList(List([BLSFieldElement for _ in range(CHUNKS_PER_BLOB)]), max_length=MAX_BLOBS_PER_BLOCK))
    )