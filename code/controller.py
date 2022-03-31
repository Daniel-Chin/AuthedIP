from socket import socket
import rsa
from shared import *

class Controller:
    def __init__(self) -> None:
        self.rsa_public_key = ...       # pre-configured
        self.rsa_private_key = ...      # pre-configured

        self.known_public_keys = ...    
        # contains all valid public keys in the enterprise. 
    
    def relaySubscription(
        self, action, verifier_ip, router_ip, 
    ):
        s = socket()
        s.connect((router_ip, 2333))

        # authenticate
        noise = s.recv(HASH_LEN)
        signed_noise = rsa.sign_hash(
            noise, self.rsa_private_key, HASH_METHOD, 
        )
        s.send(signed_noise)

        # relay command
        s.send(( action, verifier_ip ))
        # assert s.recv(2) == b'ok'
        s.close()
