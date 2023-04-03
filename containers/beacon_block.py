from rlp import Serializable
from rlp.sedes import CountableList

from config import *
from containers.beacon_ops import ProposerSlashing, AttesterSlashing
from containers.attestation import Attestation
from containers.execution_payload import ExecutionPayload

class BeaconBlockBody(Serializable):
    '''
    BeaconBlockBody resides in a BeaconBlock.
    '''
    
    fields = (
        ('randao_reveal', BLSSignature),

        # Operations
        ('proposer_slashings', CountableList(ProposerSlashing, max_length=MAX_PROPOSER_SLASHINGS)),
        ('attester_slashings', CountableList(AttesterSlashing, max_length=MAX_ATTESTER_SLASHINGS)),
        ('attestations', CountableList(Attestation, max_length=MAX_ATTESTATIONS)),

        # Execution
        ('execution_payload', ExecutionPayload),
    )


class BeaconBlock(Serializable):
    '''
    BeaconBlock is used to communicate network updates to all the other validators, 
    and those validators update their own BeaconState by applying BeaconBlocks.
    '''

    fields = (
        ('slot', Slot),
        ('proposer_index', ValidatorIndex),
        ('parent_root', Root),
        ('state_root', Root),
        ('body', BeaconBlockBody),
    )


class BeaconBlockHeader(Serializable):
    '''
    Used in the BeaconState
    '''

    fields = (
        ('slot', Slot),
        ('proposer_index', ValidatorIndex),
        ('parent_root', Root),
        ('state_root', Root),
        ('body_root', Root),
    )


class SignedBeaconBlock(Serializable):
    '''
    Used for slashing
    '''

    fields = (
        ('message', BeaconBlock),
        ('signature', BLSSignature)
    )


class SignedBeaconBlockHeader(Serializable):
    '''
    Used for slashing
    '''

    fields = (
        ('message', BeaconBlockHeader),
        ('signature', BLSSignature)
    )