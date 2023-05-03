from rlp import Serializable

from config import *

class SigningData(Serializable):
    '''
    This is just a convenience container, used only in compute_signing_root() to calculate the hash tree root of an object along with a domain. 
    The resulting root is the message data that gets signed with a BLS signature. 
    The SigningData object itself is never stored or transmitted.
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        ('object_root', Root()),
        ('domain', Domain())
    )