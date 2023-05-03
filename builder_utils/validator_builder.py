from config import *

from containers.validator import Validator

def build_validator(pubkey: BLSPubkey, effective_balance: Gwei, slashed: boolean) -> Validator:
    
    return Validator(pubkey=pubkey, effective_balance=effective_balance, slashed=slashed)