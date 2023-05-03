from rlp import Serializable
from rlp.sedes import boolean, CountableList

from config import *
from containers.checkpoint import Checkpoint

class AttestationData(Serializable):
    '''
    This is the fundamental unit of attestation data. 
    Attestations from (committees of) validators are used to provide votes simultaneously 
    for each of the LMD GHOST & Casper FFG consensus mechanisms.
    '''

    Serializable._in_mutable_context = True

    fields = (
        ('slot', Slot()),
        ('index', CommitteeIndex()),

        # LMD GHOST vote
        ('beacon_block_root', Root()),

        # FFG vote
        ('source', Checkpoint),
        ('target', Checkpoint),
    )

    
class Attestation(Serializable):
    '''
    This is the form in which attestations make their way around the network. 
    Attestations containing identical AttestationData can be combined into a 
    single attestation by aggregating the signatures.
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        # bit-list indicating all validators that have attested to the required data 
        ('aggregation_bits', CountableList(boolean, max_length=MAX_VALIDATORS_PER_COMMITTEE)),
        ('data', AttestationData),
        ('signature', BLSSignature),
    )


class IndexedAttestation(Serializable):
    '''
    This is one of the forms in which aggregated attestations 
    (combined identical attestations from multiple validators in the same committee) are handled.
    Used for attester slashing
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        # list of indices of validators based on the global validator registry
        ('aggregation_bits', CountableList(ValidatorIndex(), max_length=MAX_VALIDATORS_PER_COMMITTEE)),
        ('data', AttestationData),
        ('signature', BLSSignature()),
    )



class AggregateAndProof(Serializable):
    '''
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        ('aggregator_index', ValidatorIndex()),
        ('aggregate', Attestation),
        ('selection_proof', BLSSignature()),
    )


class SignedAggregateAndProof(Serializable):
    '''
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        ('message', AggregateAndProof),
        ('signature', BLSSignature()),
    )
