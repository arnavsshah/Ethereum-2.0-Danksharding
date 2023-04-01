from typing import List

from config.custom_constants import *
from config.custom_presets import *
from config.custom_types import *

from beacon_ops import ProposerSlashing, AttesterSlashing
from attestation import Attestation
from execution_payload import ExecutionPayload

class BeaconBlockBody():
    '''
    BeaconBlockBody resides in a BeaconBlock.
    '''
    randao_reveal: BLSSignature

    # Operations
    # Length <= MAX_PROPOSER_SLASHINGS
    proposer_slashings: List[ProposerSlashing]
    # Length <= MAX_ATTESTER_SLASHINGS
    attester_slashings: List[AttesterSlashing]
    # Length <= MAX_ATTESTATIONS
    attestations: List[Attestation]

    # Execution
    execution_payload: ExecutionPayload



class BeaconBlock():
    '''
    BeaconBlock is used to communicate network updates to all the other validators, 
    and those validators update their own BeaconState by applying BeaconBlocks.
    '''
    slot: Slot
    proposer_index: ValidatorIndex
    parent_root: Root
    state_root: Root
    body: BeaconBlockBody


class BeaconBlockHeader():
    '''
    Used in the BeaconState
    '''
    slot: Slot
    proposer_index: ValidatorIndex
    parent_root: Root
    state_root: Root
    body_root: Root


class SignedBeaconBlockHeader():
    '''
    Used for slashing
    '''
    message: BeaconBlockHeader
    signature: BLSSignature