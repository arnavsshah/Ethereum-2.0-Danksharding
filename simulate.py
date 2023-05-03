import pickle

from utils.create_txns import create_txns
from utils.create_genesis import create_genesis

from node import Node



# 4 slots per epoch
# 6 secs per slot
# 3 validators per committee
# 1 committee per slot

if __name__ == '__main__':
    create_txns()
    genesis_beacon_block, genesis_beacon_state = create_genesis()

    bls_public_keys_file = 'data/bls_public_keys.pkl'
    bls_private_keys_file = 'data/bls_private_keys.pkl'

    with open(bls_public_keys_file, 'rb') as f:
        validator_bls_public_keys = pickle.load(f)
    
    with open(bls_private_keys_file, 'rb') as f:
        validator_bls_private_keys = pickle.load(f)
    

    a = Node(validator_bls_private_keys[0], validator_bls_public_keys[0], genesis_beacon_block, genesis_beacon_state)
