from config import *

from helper_funcs.misc import hash

from typing import List

def blob_to_kzg(blob: List[BLSFieldElement, CHUNKS_PER_BLOB]) -> KZGCommitment:
    computed_kzg = bls.Z1
    for value, point_kzg in zip(tx.blob, KZG_SETUP_LAGRANGE):
        assert value < BLS_MODULUS
        computed_kzg = bls.add(
            computed_kzg,
            bls.multiply(point_kzg, value)
        )
    return computed_kzg


def kzg_to_versioned_hash(kzg: KZGCommitment) -> VersionedHash:
    return BLOB_COMMITMENT_VERSION_KZG + hash(kzg)[1:]


def verify_kzg_proof(polynomial_kzg: KZGCommitment,
                     x: BLSFieldElement,
                     y: BLSFieldElement,
                     quotient_kzg: KZGCommitment):
    # Verify: P - y = Q * (X - x)
    X_minus_x = bls.add(KZG_SETUP_G2[1], bls.multiply(bls.G2, BLS_MODULUS - x))
    P_minus_y = bls.add(polynomial_kzg, bls.multiply(bls.G1, BLS_MODULUS - y))
    return bls.pairing_check([
        [P_minus_y, bls.neg(bls.G2)],
        [quotient_kzg, X_minus_x]
    ])