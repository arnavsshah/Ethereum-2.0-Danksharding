from typing import List, Tuple, Dict
import random
import pickle

from rlp import encode, decode

from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
from hashlib import sha256 as H

from bls.scheme import setup, ttp_keygen

from containers.transaction import BlobTransaction, SignedBlobTransaction

NUM_ACCS = 40
NUM_TXNS = 1000
INIT_BALANCE = 100

NUM_VALIDATORS = 12  # 4(3), 4 slots, 3 vals per slot/committee (so, need 2/3 majority or t=2, n=12 for BLS)
BLS_THRESHOLD = 2


def generate_txn_key_pair(num_acc: int) -> Tuple[List[bytes], List[bytes]]:
    '''
    Creates a list of 'num_acc' public-private key-pairs used for signing transactions
    '''
    
    str_private_keys, str_public_keys = [], []

    for _ in range(num_acc):
        signing_key = SigningKey.generate()
        verify_key = signing_key.verify_key

        str_signing_key = signing_key.encode(encoder=HexEncoder)
        str_verify_key = verify_key.encode(encoder=HexEncoder)

        str_private_keys.append(str_signing_key)
        str_public_keys.append(str_verify_key)
    
    return str_private_keys, str_public_keys


def generate_bls_key_pair(num_validators: int, threshold: int) -> Tuple[List[str], List[bytes]]:
    '''
    Creates a list of threshold-out-of-num_validators BLS public-private key-pairs used for attestation on the beacon chain
    '''
    
    params = setup()
    signing_keys, verify_keys = ttp_keygen(params, threshold, num_validators)

    str_signing_keys, str_verify_keys = [], []
    for signing_key, verify_key in zip(signing_keys, verify_keys):
        str_signing_keys.append(str(signing_key))
        str_verify_keys.append(HexEncoder.encode(verify_key.export()))

    return str_signing_keys, str_verify_keys, params


# TODO - remove infinte loop later
def create_txn(private_keys: List[bytes], public_keys: List[bytes], 
            txn_acc_balance: Dict[bytes, int], txn_acc_nonce: Dict[bytes, int]) -> bytes:
    
    '''
    Creates a single transactions using a random sender and receiver from the list of public keys and a
    random and valid value based on the account's balance 
    '''

    while True:
        sender_index = random.choice(range(len(private_keys)))
        sender = public_keys[sender_index]
        
        while True:
            receiver_index = random.choice(range(len(private_keys)))
            receiver = public_keys[receiver_index]
            if sender != receiver:
                break

        value = random.randint(1, 5)

        if txn_acc_balance[sender] >= value:
            txn_acc_balance[sender] -= value
            txn_acc_balance[receiver] += value

            txn = BlobTransaction(nonce=txn_acc_nonce[sender],
                                max_fee_per_gas=1,
                                gas_limit=10,
                                sender=sender,
                                receiver=receiver,
                                value=value)
            
            txn_acc_nonce[sender] += 1

            sender_sk = SigningKey(private_keys[sender_index], encoder=HexEncoder)

            signature = sender_sk.sign(encode(txn, BlobTransaction), encoder=HexEncoder).signature
            signed_txn = SignedBlobTransaction(message=txn, signature=signature)

            return encode(signed_txn, SignedBlobTransaction)


def create_txns(txn_private_keys_file: str = 'data/txn_private_keys.pkl',
                txn_public_keys_file: str = 'data/txn_public_keys.pkl',
                bls_private_keys_file: str = 'data/bls_private_keys.pkl',
                bls_public_keys_file: str = 'data/bls_public_keys.pkl',
                params_file: str = 'data/public_params.pkl',
                txns_file: str = 'data/txns.pkl') -> None:
    '''
    Writes transasctions key-pairs, BLS key-pairs and transactions to a pickle file
    '''
    
    num_acc = NUM_ACCS
    num_txns = NUM_TXNS
    init_balance = INIT_BALANCE

    num_validators = NUM_VALIDATORS
    threshold = BLS_THRESHOLD

    signed_txns = []
    txn_private_keys, txn_public_keys = generate_txn_key_pair(num_acc)
    bls_private_keys, bls_public_keys, params = generate_bls_key_pair(num_validators, threshold)

    txn_acc_balance = {txn_public_key: init_balance for txn_public_key in txn_public_keys}
    txn_acc_nonce = {txn_public_key: 0 for txn_public_key in txn_public_keys}

    for _ in range(num_txns):
        signed_txns.append(create_txn(txn_private_keys, txn_public_keys, txn_acc_balance, txn_acc_nonce))


    with open(txn_private_keys_file, 'wb') as f:
        pickle.dump(txn_private_keys, f)

    with open(txn_public_keys_file, 'wb') as f:
        pickle.dump(txn_public_keys, f)

    with open(bls_private_keys_file, 'wb') as f:
        pickle.dump(bls_private_keys, f)

    with open(bls_public_keys_file, 'wb') as f:
        pickle.dump(bls_public_keys, f)

    # with open(params_file, 'wb') as f:
    #     pickle.dump(params, f)

    with open(txns_file, 'wb') as f:
        pickle.dump(signed_txns, f)

    
    
