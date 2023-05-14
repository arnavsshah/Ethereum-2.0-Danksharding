import threading
import threading
from termcolor import cprint
from collections import defaultdict
from queue import Queue

from rlp import encode, decode

from config import *

from helper_funcs.math import bytes_to_int
from helper_funcs.misc import hash, hash_tree_root, compute_epoch_at_slot, compute_start_slot_at_epoch, compute_timestamp_at_slot, compute_epoch_at_slot, compute_signing_root
from helper_funcs.beacon_state_accesors import get_current_epoch, get_randao_mix, get_beacon_proposer_index, get_committee_count_per_slot, get_beacon_committee, get_domain, get_block_root
import helper_funcs.bls_utils as bls

from builder_utils.beacon_block_builder import build_beacon_block_body, build_beacon_block, build_signed_beacon_block, build_beacon_block_header
from builder_utils.execution_payload_builder import build_execution_payload
from builder_utils.attestation_builder import build_attestation_data, build_attestation, build_aggregate_and_proof, build_signed_aggregate_and_proof

from state_transition_funcs.state_transition import state_transition, process_slots

from containers.beacon_state import BeaconState
from containers.beacon_block import BeaconBlock, SignedBeaconBlock, BeaconBlockHeader
from containers.execution_payload import ExecutionPayload, SignedBlobTransaction
from containers.attestation import AttestationData, Attestation, AggregateAndProof, SignedAggregateAndProof
from containers.checkpoint import Checkpoint

from typing import Optional, List, Tuple


# TODO - check for rollbacks if assertion fails
class Node(threading.Thread):
    def __init__(self, id: int, privkey: str, pubkey: BLSPubkey,
                genesis_beacon_block: SignedBeaconBlock, genesis_beacon_state: BeaconState,
                main_subnet: List, proposer_subnet: List, attestation_subnets: List[List], txn_queue: Queue):
        super(Node, self).__init__()

        self.id = id

        self.privkey = privkey
        self.pubkey = pubkey

        self.genesis_beacon_block = genesis_beacon_block
        self.genesis_beacon_state = genesis_beacon_state
        
        self.genesis_epoch_flag = True
        self.genesis_slot_flag = True

        self.main_subnet = main_subnet
        self.proposer_subnet = proposer_subnet
        self.attestation_subnets = attestation_subnets

        self.txn_queue = txn_queue

        self.validator_index = self.get_validator_index()

        self.beacon_chain_head = genesis_beacon_block.copy()
        self.beacon_state = genesis_beacon_state.copy()

        self.my_proposed_blocks = {}
        self.my_attestations = {}
        self.processed_blocks = {}
        self.other_attestations = defaultdict(lambda:[])

        self.stop = False
    

    def stop_thread(self):
        self.stop = True


    # interval 1, 2: propose and braodcast block
    # interval 3, 4: attest and broadcast attestation
    # interval 5:    aggregate attestation and broadcast aggregation
    # interval 6:    update beacon state and beacon block

    def run(self) -> None:

        cprint(f'Running node {self.id}...', 'cyan')

        # start of every epoch
        def per_epoch():
            
            # handles edge case for the last slot in the genesis epoch where get_current_epoch(self.beacon_state) is still the same epoch
            if self.genesis_epoch_flag:
                curr_epoch = 0
                self.genesis_epoch_flag = False
            else:
                curr_epoch = get_current_epoch(self.beacon_state) + 1

            self.current_attestation_assignment = self.get_committee_assignment(self.beacon_state, curr_epoch)
            if self.current_attestation_assignment is not None:
                    # current epoch's attesting params
                    attesting_committee, attesting_index, attesting_slot = self.current_attestation_assignment

            epoch_timer = threading.Timer(SECONDS_PER_SLOT * SLOTS_PER_EPOCH, per_epoch)
            epoch_timer.start()


            # every slot (runs SLOTS_PER_EPOCH times)
            def per_slot():
                if per_slot.counter < SLOTS_PER_EPOCH:
                    per_slot.counter += 1

                    prev_slot = self.beacon_state.slot

                    # block at slot 0 is already proposed (genesis beacon block). Thus, skip 0th slot only
                    if not self.genesis_slot_flag:
                        curr_slot = prev_slot + 1
                    
                    per_slot.slot_timer = threading.Timer(SECONDS_PER_SLOT, per_slot)
                    per_slot.slot_timer.start()


                    # every interval (runs INTERVALS_PER_SLOT times)
                    def per_interval():
                        if per_interval.counter < INTERVALS_PER_SLOT:
                            per_interval.counter += 1
                            

                            # propose a block within the first 1/3rd of the slot
                            if 0 <= per_interval.counter < (INTERVALS_PER_SLOT / 3): 
                                temp_state = self.beacon_state.copy()
                                process_slots(temp_state, curr_slot)

                                if self.is_proposer(temp_state) and curr_slot not in self.my_proposed_blocks:
                                    block = self.propose_block(curr_slot)
                                    if block is None:
                                        cprint(f'{self.id}: No more transactions to add to blockchain at slot {curr_slot}, epoch {curr_epoch}', 'dark_grey')
                                    else:
                                        self.proposer_subnet.append(block)
                                        self.my_proposed_blocks[curr_slot] = encode(block, SignedBeaconBlock)
                                        cprint(f'{self.id}: Signed beacon block proposed for slot {curr_slot}, epoch {curr_epoch}', 'yellow')


                            if attesting_slot == curr_slot and self.current_attestation_assignment is not None:

                                # attest a block b/w 1/3rd and 2/3rd of the slot
                                if (INTERVALS_PER_SLOT / 3) < per_interval.counter < (2 * INTERVALS_PER_SLOT / 3): 
                                    
                                    # check if a block has already been attested in the given slot
                                    # check if the propoed block belongs to the attestation slot
                                    if attesting_slot not in self.my_attestations and self.proposer_subnet and self.proposer_subnet[-1].message.slot == attesting_slot:
                                        proposed_block = self.proposer_subnet[-1]

                                        # do not try to attest a block again
                                        if curr_slot not in self.processed_blocks:
                                            
                                            proposed_state = self.beacon_state.copy()

                                            try:
                                                state_transition(proposed_state, proposed_block)

                                                my_attestation = self.get_attestation(curr_slot, attesting_index, proposed_block, proposed_state)
                                                self.my_attestations[attesting_slot] = encode(my_attestation, Attestation)
                                                self.processed_blocks[curr_slot] = encode(proposed_block, SignedBeaconBlock)

                                                self.broadcast_attestation(my_attestation, proposed_state, curr_slot, curr_epoch, attesting_index)

                                                cprint(f'{self.id}: Beacon block attested for slot {curr_slot}, epoch {curr_epoch}', 'magenta')
                                                
                                            except AssertionError:
                                                cprint(f'{self.id}: Invalid block at slot {curr_slot}, epoch {curr_epoch}, proposer index: {proposed_block.message.proposer_index}', 'red')


                                # aggregate attestations of a block b/w 2/3rd and 2/3rd + 1 of the slot
                                if (2 * INTERVALS_PER_SLOT / 3) <= per_interval.counter < (1 + 2 * INTERVALS_PER_SLOT / 3): 

                                    slot_signature = self.get_slot_signature(curr_slot)

                                    if self.is_aggregator(self.beacon_state, curr_slot, attesting_index, slot_signature):

                                        latest_proposed_block = decode(self.processed_blocks[curr_slot], SignedBeaconBlock)

                                        if latest_proposed_block is not None:
                                            proposed_state = self.beacon_state.copy()

                                            try:
                                                state_transition(proposed_state, latest_proposed_block)
                                            except AssertionError:
                                                cprint(f'{self.id}: Invalid block attested to at slot {curr_slot}, epoch {curr_epoch}, proposer index: {latest_proposed_block.message.proposer_index}', 'red')
                                                return
                                            
                                            subnet_id = self.compute_subnet_for_aggregation(proposed_state, curr_slot, curr_epoch, attesting_index)
                                            
                                            new_attestation_received_flag = False
                                            for attestation in self.attestation_subnets[subnet_id][::-1]:
                                                
                                                # TODO don't traverse all attestations in the subnet 
                                                if attestation.data.slot == curr_slot and attestation not in self.other_attestations[curr_slot]:
                                                    new_attestation_received_flag = True
                                                    self.other_attestations[curr_slot].append(attestation)

                                            # node should receive new attestations
                                            # node should receive atleast 2 attestations for aggregation 
                                            # node should have attested to the proposed block itself
                                            if new_attestation_received_flag and len(self.other_attestations[curr_slot]) >= 2 and curr_slot in self.my_attestations:
                                                
                                                my_attestation = decode(self.my_attestations[curr_slot], Attestation)
                                                if my_attestation.data.slot == curr_slot:
                                                    aggregated_attestation = self.aggregate_attestations(self.other_attestations[curr_slot], my_attestation)

                                                    signed_aggregate_and_proof = self.get_signed_aggregate_and_proof(self.validator_index, aggregated_attestation)
                                                    self.main_subnet.append(signed_aggregate_and_proof)

                                                    cprint(f'{self.id}: Attestations aggregated for slot {curr_slot}, epoch {curr_epoch}', 'blue')


                            # check aggregate attestations of a block at the last interval of the slot
                            if (1 + 2 * INTERVALS_PER_SLOT / 3) <= per_interval.counter < (INTERVALS_PER_SLOT): 

                                # check if attestation is of incorrect slot
                                # check if attestation doesn't attest latest accepted beacon block
                                if self.main_subnet and self.main_subnet[-1].message.aggregate.data.slot == curr_slot and hash_tree_root(self.beacon_chain_head.message) != self.main_subnet[-1].message.aggregate.data.beacon_block_root:
                                    signed_aggregate_and_proof = self.main_subnet[-1]

                                    aggregator_index = signed_aggregate_and_proof.message.aggregator_index
                                    committee = get_beacon_committee(self.beacon_state, curr_slot, signed_aggregate_and_proof.message.aggregate.data.index)

                                    try:
                                        assert aggregator_index in committee
                                    except AssertionError:
                                        cprint(f'{self.id}: Aggregator {aggregator_index} not in attesting committee {committee} at slot {curr_slot}, epoch {curr_epoch}', 'red')
                                        return
                                    
                                    aggregator_pubkey = self.beacon_state.validators[aggregator_index].pubkey
                                    
                                    # verify that the actual selected aggregator has aggregated all attestaions
                                    try:
                                        domain = get_domain(DOMAIN_SELECTION_PROOF)
                                        signing_root = compute_signing_root(curr_slot, domain)
                                        assert bls.Verify(aggregator_pubkey, signing_root, signed_aggregate_and_proof.message.selection_proof)
                                    except AssertionError:
                                        cprint(f'{self.id}: Invalid aggregator {aggregator_index} has aggregated attestations at slot {curr_slot}, epoch {curr_epoch}', 'red')
                                        return
                                    
                                    # verify signature of signed_aggregate_and_proof
                                    try:
                                        domain = get_domain(DOMAIN_AGGREGATE_AND_PROOF)
                                        signing_root = compute_signing_root(signed_aggregate_and_proof.message, domain)
                                        assert bls.Verify(aggregator_pubkey, signing_root, signed_aggregate_and_proof.signature)
                                    except AssertionError:
                                        cprint(f'{self.id}: Invalid signature of aggregation of attestations at slot {curr_slot}, epoch {curr_epoch}, aggregator index: {aggregator_index}', 'red')
                                        return
                                    
                                    # TODO check aggregated attestation has been signed by 2/3 majority
                                    try:
                                        # attester_pubkeys = [self.beacon_state.validators[i].pubkey for i in committee]
                                        # # attester_pubkeys = [validator.pubkey for validator in self.beacon_state.validators]
                                        # domain = get_domain(DOMAIN_BEACON_ATTESTER)
                                        # signing_root = compute_signing_root(signed_aggregate_and_proof.message.aggregate.data, domain)
                                        # assert bls.FastAggregateVerify(attester_pubkeys, signing_root, signed_aggregate_and_proof.message.aggregate.signature)
                                        pass
                                    except AssertionError:
                                        cprint(f'{self.id}: 2/3rd majority not present for attestations at slot {curr_slot}, epoch {curr_epoch}, attesting committee {committee}', 'red')
                                        return
                                    
                                    proposed_block_root = signed_aggregate_and_proof.message.aggregate.data.beacon_block_root
                                    for block in self.proposer_subnet[::-1]:
                                        if hash_tree_root(block.message) == proposed_block_root:
                                            try:
                                                state_transition(self.beacon_state, block)
                                                self.beacon_chain_head = block
                                                cprint(f'{self.id}: Block at slot {curr_slot}, epoch {curr_epoch}, proposed by {block.message.proposer_index}, attested by committee {committee}', 'green', attrs=['bold'])
                                                break
                                            except AssertionError:
                                                cprint(f'{self.id}: Invalid block aggregated and attested by validators at slot {curr_slot}, epoch {curr_epoch}, proposer index: {proposed_block.message.proposer_index}', 'red')
                                                return

                        per_interval.interval_timer = threading.Timer(SECONDS_PER_SLOT / INTERVALS_PER_SLOT, per_interval)
                        per_interval.interval_timer.start()

                    
                    if not self.genesis_slot_flag:
                        per_interval.counter = 0
                        per_interval()
                    
                    # skip slot 0
                    if self.genesis_slot_flag:
                        self.genesis_slot_flag = False


            per_slot.counter = 0
            per_slot()

            if self.stop:
                epoch_timer.cancel()
                per_slot.slot_timer.cancel()
                per_slot.per_interval.interval_timer.cancel()

        per_epoch()
                     

    def get_validator_index(self) -> int:
        
        for i, validator in enumerate(self.genesis_beacon_state.validators):
            if validator.pubkey == self.pubkey:
                return i
        return None
    

    def is_proposer(self, state: BeaconState) -> bool:
        return get_beacon_proposer_index(state) == self.validator_index

    # modified to allow processing at epoch boudaries
    def get_epoch_signature(self, block: SignedBeaconBlock) -> BLSSignature:
        domain = get_domain(DOMAIN_RANDAO)
        slot = block.message.slot + 1 if (block.message.slot + 1) % SLOTS_PER_EPOCH == 0 else block.message.slot
        signing_root = compute_signing_root(compute_epoch_at_slot(slot), domain)
        return bls.Sign(self.privkey, signing_root)


    def get_blob_transactions(self) -> List[SignedBlobTransaction]:
        blob_transactions = []
        for _ in range(10):
            if not self.txn_queue.empty():
                blob_transactions.append(decode(self.txn_queue.get(), SignedBlobTransaction))

        return blob_transactions


    def get_execution_payload(self, slot: Slot) -> ExecutionPayload:

        parent_hash = self.beacon_state.latest_execution_payload_header.block_hash
        fee_recipient = b'stub'
        state_root = b'stub'
        prev_randao = get_randao_mix(self.beacon_state, get_current_epoch(self.beacon_state))
        gas_limit = 0
        gas_used = 0
        timestamp = compute_timestamp_at_slot(self.beacon_state, slot)
        base_fee_per_gas = 0

        blob_transactions = self.get_blob_transactions()
        if not blob_transactions:
            return None

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


    def get_block_signature(self, block: BeaconBlock) -> BLSSignature:
        domain = get_domain(DOMAIN_BEACON_PROPOSER)
        signing_root = compute_signing_root(block, domain)
        return bls.Sign(self.privkey, signing_root)


    def propose_block(self, slot: Slot) -> SignedBeaconBlock:

        randao_reveal = self.get_epoch_signature(self.beacon_chain_head)
        proposer_slashings = []
        attester_slashings = []
        attestations = []

        execution_payload = self.get_execution_payload(slot)
        if execution_payload is None:
            return None
        
        beacon_block_body = build_beacon_block_body(randao_reveal=randao_reveal,
                                                    proposer_slashings=proposer_slashings,
                                                    attester_slashings=attester_slashings,
                                                    attestations=attestations,
                                                    execution_payload=execution_payload)
        
        proposer_index = self.validator_index
        parent_root = hash_tree_root(build_beacon_block_header(self.beacon_chain_head.message))
        stub_state_root = b'stub'

        beacon_block = build_beacon_block(slot=slot,
                                        proposer_index=proposer_index,
                                        parent_root=parent_root,
                                        state_root=stub_state_root,  # stub state root
                                        body=beacon_block_body)

        state_root = self.compute_new_state_root(self.beacon_state, beacon_block)
        beacon_block.state_root = state_root
        # beacon_block.body.execution_payload.state_root = state_root

        signature = self.get_block_signature(beacon_block)

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
            return hash_tree_root(head_block.message)
        else: 
            return get_block_root(head_state, get_current_epoch(head_state))


    def get_attestation_signature(self, state: BeaconState, attestation_data: AttestationData) -> BLSSignature:
        
        domain = get_domain(DOMAIN_BEACON_ATTESTER)
        signing_root = compute_signing_root(attestation_data, domain)
        return bls.Sign(self.privkey, signing_root)


    def get_attestation(self, slot: Slot, index: CommitteeIndex, 
                        head_block: SignedBeaconBlock, head_state: BeaconState) -> Attestation:
        
        beacon_block_root = hash_tree_root(head_block.message)
        epoch_boundary_block_root = self.get_epoch_boundary_block_root(head_block, head_state)

        source = head_state.current_justified_checkpoint
        target = Checkpoint(epoch=get_current_epoch(head_state), root=epoch_boundary_block_root)

        attestation_data = build_attestation_data(slot, index, beacon_block_root, source, target)

        committee = get_beacon_committee(head_state, slot, index)
        aggregation_bits = [False for _ in range(len(committee))]
        aggregation_bits[committee.index(self.validator_index)] = True

        attestation_signature = self.get_attestation_signature(head_state, attestation_data)
        
        attestation = build_attestation(aggregation_bits, attestation_data, attestation_signature)

        return attestation


    def compute_subnet_for_attestation(self, committees_per_slot: int, slot: Slot, committee_index: CommitteeIndex) -> int:
        """
        Compute the correct subnet for an attestation for Phase 0.
        Note, this mimics expected future behavior where attestations will be mapped to their shard subnet.
        """
        
        slots_since_epoch_start = int(slot % SLOTS_PER_EPOCH)
        committees_since_epoch_start = committees_per_slot * slots_since_epoch_start

        return (committees_since_epoch_start + committee_index) % ATTESTATION_SUBNET_COUNT


    def compute_subnet_for_aggregation(self, state: BeaconState, slot: Slot, epoch: Epoch, committee_index: CommitteeIndex) -> int:
        """
        Compute the correct subnet for an attestation for Phase 0.
        Note, this mimics expected future behavior where attestations will be mapped to their shard subnet.
        """
        
        committees_per_slot = get_committee_count_per_slot(state, epoch)
        slots_since_epoch_start = int(slot % SLOTS_PER_EPOCH)
        committees_since_epoch_start = committees_per_slot * slots_since_epoch_start

        return (committees_since_epoch_start + committee_index) % ATTESTATION_SUBNET_COUNT


    def broadcast_attestation(self, attestation: Attestation, state: BeaconState,
                            slot: Slot, epoch: Epoch, index: CommitteeIndex) -> None:

        committees_per_slot = get_committee_count_per_slot(state, epoch)
        subnet_id = self.compute_subnet_for_attestation(committees_per_slot, slot, index)

        self.attestation_subnets[subnet_id].append(attestation)


    def get_slot_signature(self, slot: Slot) -> BLSSignature:
        
        domain = get_domain(DOMAIN_SELECTION_PROOF)
        signing_root = compute_signing_root(slot, domain)
        return bls.Sign(self.privkey, signing_root)


    # https://docs.google.com/spreadsheets/d/1C7pBqEWJgzk3_jesLkqJoDTnjZOODnGTOJUrxUMdxMA/edit#gid=0
    # with len(committee) = 3 and TARGET_AGGREGATORS_PER_COMMITTEE = 1, 
    # modulo = 1
    # chance of 1 validator gets selected = 1
    # Expected len(selected_validators) = 3 * 1 = 3
    # Chance of no aggregator = (1-1)^3 = 0
    def is_aggregator(self, state: BeaconState, slot: Slot, index: CommitteeIndex, slot_signature: BLSSignature) -> bool:
        
        committee = get_beacon_committee(state, slot, index)
        modulo = max(1, len(committee) // TARGET_AGGREGATORS_PER_COMMITTEE)
        return bytes_to_int(hash(slot_signature)[0:8]) % modulo == 0
    

    def get_aggregate_signature(self, attestations: List[Attestation]) -> BLSSignature:
        signatures = [attestation.signature for attestation in attestations]
        return bls.Aggregate(signatures)

    
    def aggregate_attestations(self, attestations: List[Attestation], my_attestation: Attestation) -> Attestation:
        
        assert len(attestations) > 0, '0 attestations found during aggregation'

        aggregation_bits = list(my_attestation.aggregation_bits)
        
        for attestation in attestations:
            if attestation.data == my_attestation.data:
                validator_index_in_committee = attestation.aggregation_bits.index(True)
                aggregation_bits[validator_index_in_committee] = True
        
        aggregation_signature = self.get_aggregate_signature(attestations)

        aggregate_attestation = build_attestation(aggregation_bits, my_attestation.data, aggregation_signature)

        return aggregate_attestation

    
    def get_aggregate_and_proof(self, aggregator_index: ValidatorIndex, aggregate: Attestation) -> AggregateAndProof:
        
        selection_proof = self.get_slot_signature(aggregate.data.slot)
        aggregate_and_proof = build_aggregate_and_proof(aggregator_index, aggregate, selection_proof)
        return aggregate_and_proof
    

    def get_aggregate_and_proof_signature(self, aggregate_and_proof: AggregateAndProof) -> BLSSignature:
        
        domain = get_domain(DOMAIN_AGGREGATE_AND_PROOF)
        signing_root = compute_signing_root(aggregate_and_proof, domain)
        return bls.Sign(self.privkey, signing_root)


    def get_signed_aggregate_and_proof(self, validator_index: ValidatorIndex, aggregate_attestation: Attestation) -> SignedAggregateAndProof:
        
        aggregate_and_proof = self.get_aggregate_and_proof(validator_index, aggregate_attestation)
        aggregate_and_proof_signature = self.get_aggregate_and_proof_signature(aggregate_and_proof)
        signed_aggregate_and_proof = build_signed_aggregate_and_proof(aggregate_and_proof, aggregate_and_proof_signature)
        return signed_aggregate_and_proof
