from bls.scheme import setup, sign, verify, aggregate_vk, aggregate_sigma
from bplib.bp import BpGroup, G1Elem, G2Elem
from petlib.bn import Bn
from typing import List

from config import *


def Sign(privkey: int, message: bytes) -> BLSSignature:
    params = setup() # generate the public parameters

    privkey_bignumber = Bn.from_decimal(str(privkey))

    return sign(params, privkey_bignumber, message).export()


def Verify(pubkey: BLSPubkey, message: bytes, signature: BLSSignature) -> bool:
    params = setup() # generate the public parameters
    G = BpGroup()

    signature_grp_elem = G1Elem.from_bytes(signature, G)  # convert to bplib.bp.G1Elem as required by the bls library 
    pubkey_grp_elem = G2Elem.from_bytes(pubkey, G)  # convert to bplib.bp.G2Elem as required by the bls library 
    
    return verify(params, pubkey_grp_elem, signature_grp_elem, message)


def Aggregate(signatures: List[BLSSignature]) -> BLSSignature:
    params = setup() # generate the public parameters
    G = BpGroup()
    
    signatures_grp_elems = [G1Elem.from_bytes(signature, G) for signature in signatures]  # convert to bplib.bp.G1Elem as required by the bls library 
    
    return aggregate_sigma(params, signatures_grp_elems).export()


def FastAggregateVerify(pubkeys: List[BLSPubkey], message: bytes, signature: BLSSignature) -> bool:
    params = setup() # generate the public parameters
    G = BpGroup()
    
    signature_grp_elem = G1Elem.from_bytes(signature, G)  # convert to bplib.bp.G1Elem as required by the bls library 
    pubkey_grp_elems = [G2Elem.from_bytes(pubkey, G) for pubkey in pubkeys]   # convert to bplib.bp.G2Elem as required by the bls library 
    
    aggr_pubkeys = aggregate_vk(params, pubkey_grp_elems) # aggregate public keys
    return verify(params, aggr_pubkeys, signature_grp_elem, message)


def KeyValidate(pubkey: BLSPubkey) -> bool:
    G = BpGroup()
    try:
        pubkey_grp_elem = G2Elem.from_bytes(pubkey, G)  # check if conversion to bplib.bp.G2Elem works 
        return True
    except:
        return False
