from functools import lru_cache

import rsa

from shared import *

class User:
    def __init__(self) -> None:
        # The RSA public key is registered with the Controller. 
        self.pubKey: rsa. PublicKey = ...
        self.priKey: rsa.PrivateKey = ...
    
    @lru_cache(1)
    def pubKeyId(self):
        return key2Id(self.pubKey)

def key2Id(pubKey: rsa.PublicKey):
    return pubKey.n.to_bytes(
        RSA_KEY_BITS // 8, ENDIAN, 
    )[- RSA_KEY_ID_BITS // 8 :]
