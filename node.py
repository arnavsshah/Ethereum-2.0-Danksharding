import threading

from config import *

from helper_funcs.math import bytes_to_int
from helper_funcs.misc import hash_tree_root, compute_start_slot_at_epoch, compute_timestamp_at_slot, compute_epoch_at_slot, compute_signing_root
from helper_funcs.beacon_state_accesors import get_current_epoch, get_randao_mix, get_beacon_proposer_index, get_committee_count_per_slot, get_beacon_committee, get_domain, get_block_root
import helper_funcs.bls_utils as bls

from builder_utils.beacon_block_builder import build_beacon_block_body, build_beacon_block, build_signed_beacon_block
from builder_utils.execution_payload_builder import build_execution_payload
from builder_utils.attestation_builder import build_attestation_data, build_attestation, build_aggregate_and_proof, build_signed_aggregate_and_proof

from state_transition_funcs.state_transition import state_transition

from containers.beacon_state import BeaconState
from containers.beacon_block import BeaconBlock, SignedBeaconBlock
from containers.execution_payload import ExecutionPayload, SignedBlobTransaction
from containers.attestation import AttestationData, Attestation, AggregateAndProof, SignedAggregateAndProof
from containers.checkpoint import Checkpoint

from typing import Optional, List, Tuple


class Node():
    def __init__(self, privkey, pubkey, 
                genesis_beacon_block, genesis_beacon_state,
                subnets):
        super(Node, self).__init__()

        self.privkey = privkey
        self.pubkey = pubkey

        self.genesis_beacon_block = genesis_beacon_block
        self.genesis_beacon_state = genesis_beacon_state

        self.subnets = subnets

        self.validator_index = self.get_validator_index()

        self.beacon_chain_head = genesis_beacon_block
        self.beacon_state = genesis_beacon_state


    def get_validator_index(self) -> int:
        
        for i, validator in enumerate(self.genesis_beacon_state.validators):
            if validator.pubkey == self.pubkey:
                return i
        return None
    

    def is_proposer(self, state: BeaconState) -> bool:
        
        return get_beacon_proposer_index(state) == self.validator_index


    def get_epoch_signature(self, state: BeaconState, block: BeaconBlock) -> BLSSignature:
        
        domain = get_domain(state, DOMAIN_RANDAO, compute_epoch_at_slot(block.slot))
        signing_root = compute_signing_root(compute_epoch_at_slot(block.slot), domain)
        return bls.Sign(self.privkey, signing_root)


    # TODO
    def get_blob_transactions(self) -> List[SignedBlobTransaction]:    
        return []


    def get_execution_payload(self, slot: Slot) -> ExecutionPayload:

        parent_hash = self.beacon_state.latest_execution_payload_header.block_hash
        fee_recipient = b'do not care'
        state_root = None  # TODO
        prev_randao = get_randao_mix(self.beacon_state, get_current_epoch(self.beacon_state))
        gas_limit = 0
        gas_used = 0
        timestamp = compute_timestamp_at_slot(self.beacon_state, slot)
        base_fee_per_gas = 0
        blob_transactions = self.get_blob_transactions()

        execution_payload = build_execution_payload(parent_hash=parent_hash, 
                                                fee_recipient=fee_recipient, 
                                                state_root=state_root,
                                                prev_randao=prev_randao,
                                                gas_limit=gas_limit,
                                                gas_used=gas_used, 
                                                timestamp=timestamp, 
                                                base_fee_per_gas=base_fee_per_gas,
                                                blob_transactions=blob_transactions)
        
        return execution_payload


    def compute_new_state_root(self, state: BeaconState, block: BeaconBlock) -> Root:
        
        temp_state = state.copy()
        signed_block = build_signed_beacon_block(message=block, signature=b'stub')
        state_transition(temp_state, signed_block, validate_result=False)
        return hash_tree_root(temp_state)


    def get_block_signature(self, state: BeaconState, block: BeaconBlock) -> BLSSignature:
        
        domain = get_domain(state, DOMAIN_BEACON_PROPOSER, compute_epoch_at_slot(block.slot))
        signing_root = compute_signing_root(block, domain)
        return bls.Sign(self.privkey, signing_root)


    def propose_block(self, slot: Slot) -> SignedBeaconBlock:
        
        randao_reveal = self.get_epoch_signature(self.beacon_state, self.beacon_chain_head)
        proposer_slashings = []
        attester_slashings = []
        attestations = []
        execution_payload = self.get_execution_payload(slot)

        beacon_block_body = build_beacon_block_body(randao_reveal=randao_reveal,
                                                proposer_slashings=proposer_slashings,
                                                attester_slashings=attester_slashings,
                                                attestations=attestations,
                                                execution_payload=execution_payload)
        
        proposer_index = self.validator_index
        parent_root = hash_tree_root(self.beacon_chain_head)
        stub_state_root = b'stub'

        beacon_block = build_beacon_block(slot=slot,
                                        proposer_index=proposer_index,
                                        parent_root=parent_root,
                                        state_root=stub_state_root,  # stub state root
                                        body=beacon_block_body)
        
        state_root = self.compute_new_state_root(self.beacon_state, beacon_block)
        signature = self.get_block_signature(self.beacon_state, beacon_block)

        beacon_block.state_root = state_root

        signed_beacon_block = build_signed_beacon_block(message=beacon_block, signature=signature)

        return signed_beacon_block


    def get_committee_assignment(self, state: BeaconState, epoch: Epoch) -> Optional[Tuple[List[ValidatorIndex], CommitteeIndex, Slot]]:
        """
        Return the committee assignment in the ``epoch`` for ``validator_index``.
        ``assignment`` returned is a tuple of the following form:
            * ``assignment[0]`` is the list of validators in the committee
            * ``assignment[1]`` is the index to which the committee is assigned
            * ``assignment[2]`` is the slot at which the committee is assigned
        Return None if no assignment.
        """
        
        next_epoch = get_current_epoch(state) + 1
        assert epoch <= next_epoch

        start_slot = compute_start_slot_at_epoch(epoch)
        committee_count_per_slot = get_committee_count_per_slot(state, epoch)
        for slot in range(start_slot, start_slot + SLOTS_PER_EPOCH):
            for index in range(committee_count_per_slot):
                committee = get_beacon_committee(state, slot, index)
                if self.validator_index in committee:
                    return committee, index, slot
        return None


    def get_epoch_boundary_block_root(self, head_block: SignedBeaconBlock, head_state: BeaconState) -> Root:
        
        start_slot = compute_start_slot_at_epoch(get_current_epoch(head_state))
        if start_slot == head_state.slot:
            return hash_tree_root(head_block)
        else: 
            return get_block_root(self.beacon_state, get_current_epoch(head_state))


    def get_attestation_signature(self, state: BeaconState, attestation_data: AttestationData) -> BLSSignature:
        
        domain = get_domain(state, DOMAIN_BEACON_ATTESTER, attestation_data.target.epoch)
        signing_root = compute_signing_root(attestation_data, domain)
        return bls.Sign(self.privkey, signing_root)


    def get_attestation(self, slot: Slot, index: CommitteeIndex, 
                        head_block: SignedBeaconBlock, head_state: BeaconState) -> AttestationData:
        
        beacon_block_root = hash_tree_root(head_block)
        epoch_boundary_block_root = self.get_epoch_boundary_block_root(head_block, head_state)

        source = head_state.current_justified_checkpoint
        target = Checkpoint(epoch=get_current_epoch(head_state), root=epoch_boundary_block_root)

        attestation_data = build_attestation_data(slot, index, beacon_block_root, source, target)

        committee = get_beacon_committee(head_state, slot, index)
        aggregation_bits = [False for _ in range(len(committee))]
        aggregation_bits[self.validator_index] = True

        attestation_signature = self.get_attestation_signature(head_state, attestation_data)

        attestation = build_attestation(aggregation_bits, attestation_data, attestation_signature)

        return attestation


    def compute_subnet_for_attestation(committees_per_slot: int, slot: Slot, committee_index: CommitteeIndex) -> int:
        """
        Compute the correct subnet for an attestation for Phase 0.
        Note, this mimics expected future behavior where attestations will be mapped to their shard subnet.
        """
        
        slots_since_epoch_start = int(slot % SLOTS_PER_EPOCH)
        committees_since_epoch_start = committees_per_slot * slots_since_epoch_start

        return (committees_since_epoch_start + committee_index) % ATTESTATION_SUBNET_COUNT


    def broadcast_attestation(self, attestation: Attestation, state: BeaconState,
                            slot: Slot, epoch: Epoch, index: CommitteeIndex) -> None:

        committees_per_slot = get_committee_count_per_slot(state, epoch)
        subnet_id = self.compute_subnet_for_attestation(committees_per_slot, slot, index)

        self.subnets[subnet_id].put(attestation)


    def get_slot_signature(self, state: BeaconState, slot: Slot) -> BLSSignature:
        
        domain = get_domain(state, DOMAIN_SELECTION_PROOF, compute_epoch_at_slot(slot))
        signing_root = compute_signing_root(slot, domain)
        return bls.Sign(self.privkey, signing_root)


    def is_aggregator(self, state: BeaconState, slot: Slot, index: CommitteeIndex, slot_signature: BLSSignature) -> bool:
        
        committee = get_beacon_committee(state, slot, index)
        modulo = max(1, len(committee) // TARGET_AGGREGATORS_PER_COMMITTEE)
        return bytes_to_int(hash(slot_signature)[0:8]) % modulo == 0
    

    def get_aggregate_signature(self, attestations: List[Attestation]) -> BLSSignature:
        
        signatures = [attestation.signature for attestation in attestations]
        return bls.Aggregate(signatures)

    
    def aggregate_attestations(self, attestations: List[Attestation], my_attestation: Attestation) -> Attestation:
        
        assert len(attestations) > 0, '0 attestations found during aggregation'

        aggregation_bits = my_attestation.aggregation_bits

        for attestation in attestations:
            if attestation.data == my_attestation.data:
                validator_index = attestation.aggregation_bits.index(True)
                aggregation_bits[validator_index] = True

        aggregation_signature = self.get_aggregate_signature(attestations)

        aggregate_attestation = build_attestation(aggregation_bits, my_attestation.data, aggregation_signature)

        return aggregate_attestation

    
    def get_aggregate_and_proof(self, state: BeaconState, 
                                aggregator_index: ValidatorIndex, aggregate: Attestation) -> AggregateAndProof:
        
        selection_proof = self.get_slot_signature(state, aggregate.data.slot)
        aggregate_and_proof = build_aggregate_and_proof(aggregator_index, aggregate, selection_proof)
        return aggregate_and_proof
    

    def get_aggregate_and_proof_signature(self, state: BeaconState, aggregate_and_proof: AggregateAndProof) -> BLSSignature:
        
        aggregate = aggregate_and_proof.aggregate
        domain = get_domain(state, DOMAIN_AGGREGATE_AND_PROOF, compute_epoch_at_slot(aggregate.data.slot))
        signing_root = compute_signing_root(aggregate_and_proof, domain)
        return bls.Sign(self.privkey, signing_root)


    def get_signed_aggregate_and_proof(self, state: BeaconState, 
                                    validator_index: ValidatorIndex, aggregate_attestation: Attestation) -> SignedAggregateAndProof:
        
        aggregate_and_proof = self.get_aggregate_and_proof(state, validator_index, aggregate_attestation)
        aggregate_and_proof_signature = self.get_aggregate_and_proof_signature(state, aggregate_and_proof)
        signed_aggregate_and_proof = build_signed_aggregate_and_proof(aggregate_and_proof, aggregate_and_proof_signature)
        return signed_aggregate_and_proof