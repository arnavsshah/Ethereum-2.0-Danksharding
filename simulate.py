import pickle
import time

from config import *

from utils.create_txns import create_txns
from utils.create_genesis import create_genesis

from node import Node

from rlp import encode
from bls.scheme import setup
from nacl.encoding import HexEncoder

from typing import List, Tuple, Set, Dict

# 4 slots per epoch
# 6 secs per slot
# 3 validators per committee
# 1 committee per slot

if __name__ == '__main__':
    # creates a public params file for BLS sigs as well
#     create_txns()
    genesis_beacon_block, genesis_beacon_state = create_genesis()

    bls_public_keys_file = 'data/bls_public_keys.pkl'
    bls_private_keys_file = 'data/bls_private_keys.pkl'

    with open(bls_public_keys_file, 'rb') as f:
        validator_bls_public_keys = pickle.load(f)
        for i in range(len(validator_bls_public_keys)):
            validator_bls_public_keys[i] = HexEncoder.decode(validator_bls_public_keys[i])

    
    with open(bls_private_keys_file, 'rb') as f:
        validator_bls_private_keys = pickle.load(f)

    main_subnet = []
    proposer_subnet = []
    attestation_subnets = [[] for _ in range(ATTESTATION_SUBNET_COUNT)]

    nodes = []
   
    for i in range(12):
        node = Node(id=i, 
                privkey=validator_bls_private_keys[i], 
                pubkey=validator_bls_public_keys[i],
                genesis_beacon_block=genesis_beacon_block.copy(), 
                genesis_beacon_state=genesis_beacon_state.copy(),
                main_subnet=main_subnet,
                proposer_subnet=proposer_subnet,
                attestation_subnets=attestation_subnets)
        nodes.append(node)
        
    for node in nodes:
        node.start()

    time.sleep(100)

    for node in nodes:
        node.stop_thread()