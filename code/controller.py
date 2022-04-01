from socket import socket

from shared import *

class Controller:
    def __init__(self) -> None:
        self.ip_addr: Addr = ...

        # all valid public keys in the enterprise. 
        self.known_public_keys = ...    

        self.sock: socket = ...
        self.side = INSIDE
