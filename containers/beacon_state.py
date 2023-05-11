from rlp import Serializable
from rlp.sedes import big_endian_int, CountableList

from config import *

from containers.validator import Validator 
from containers.beacon_block import BeaconBlockHeader
from containers.checkpoint import Checkpoint
from containers.execution_payload import ExecutionPayloadHeader

class BeaconState(Serializable):

    Serializable._in_mutable_context = True
    
    fields = (
        # Versioning
        ('genesis_time', big_endian_int),
        ('genesis_validators_root', Root()),

        ('slot', Slot()),

        # History
        ('latest_block_header', BeaconBlockHeader),
        ('block_roots', CountableList(Root(), max_length=SLOTS_PER_HISTORICAL_ROOT)),
        ('state_roots', CountableList(Root(), max_length=SLOTS_PER_HISTORICAL_ROOT)),

        # Registry
        ('validators', CountableList(Validator, max_length=VALIDATOR_REGISTRY_LIMIT)),
        ('balances', CountableList(Gwei(), max_length=VALIDATOR_REGISTRY_LIMIT)),

        # Randomness
        ('randao_mixes', List([Bytes32() for _ in range(EPOCHS_PER_HISTORICAL_VECTOR)])),

        # Slashings
        ('slashings', CountableList(Gwei(), max_length=EPOCHS_PER_SLASHINGS_VECTOR)),  # Per-epoch sums of slashed effective balances
        
        # Participation
        ('previous_epoch_participation', CountableList(ParticipationFlags(), max_length=VALIDATOR_REGISTRY_LIMIT)),
        ('current_epoch_participation', CountableList(ParticipationFlags(), max_length=VALIDATOR_REGISTRY_LIMIT)),

        # Finality
        ('justification_bits', List([big_endian_int for _ in range(JUSTIFICATION_BITS_LENGTH)])),  # Bit set for every recent justified epoch
        ('previous_justified_checkpoint', Checkpoint),
        ('current_justified_checkpoint', Checkpoint),
        ('finalized_checkpoint', Checkpoint),

        # Execution
        ('latest_execution_payload_header', ExecutionPayloadHeader),
    )
    
    