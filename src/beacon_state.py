from typing import List

from config.custom_constants import *
from config.custom_presets import *
from config.custom_types import *

from validator import Validator 
from beacon_block import BeaconBlockHeader
from checkpoint import Checkpoint
from execution_payload import ExecutionPayloadHeader

class BeaconState():
    # Versioning
    genesis_time: int
    genesis_validators_root: Root

    slot: Slot

    # History
    latest_block_header: BeaconBlockHeader
    
    # Registry
    # Length <= VALIDATOR_REGISTRY_LIMIT
    validators: List[Validator]
    # Length <= VALIDATOR_REGISTRY_LIMIT
    balances: List[Gwei]

    # Slashings
    # Length <= EPOCHS_PER_SLASHINGS_VECTOR
    slashings: List[Gwei, EPOCHS_PER_SLASHINGS_VECTOR]  # Per-epoch sums of slashed effective balances
    
    # Participation
    previous_epoch_participation: List[ParticipationFlags]
    current_epoch_participation: List[ParticipationFlags]
    
    # Finality
    justification_bits: List[JUSTIFICATION_BITS_LENGTH]  # Bit set for every recent justified epoch
    previous_justified_checkpoint: Checkpoint
    current_justified_checkpoint: Checkpoint
    finalized_checkpoint: Checkpoint
    
    # Execution
    latest_execution_payload_header: ExecutionPayloadHeader  # [New in Bellatrix]