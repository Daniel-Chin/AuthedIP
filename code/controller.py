from socket import socket
from shared import rsaSign

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
        noise = s.recv(256)
        signed_noise = rsaSign(noise, self.rsa_private_key)
        s.send(signed_noise)

        # relay command
        s.send(( action, verifier_ip ))
        # assert s.recv(2) == b'ok'
        s.close()
