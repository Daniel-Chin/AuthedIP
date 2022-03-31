from socket import socket
from shared import *
from packet import *
from user import User

class Endhost:
    def __init__(self) -> None:
        self.ip_addr = ...

        # represents physical link
        self.sock : socket = ...

    def send(self, user : User, dest_addr, data):
        packet = AuthedIpPacket()
        packet.source_addr = self.ip_addr
        packet.  dest_addr = dest_addr
        packet.content = data

        packet.rsa_public_key_id = user.pubKeyId()
        packet.sign(user.priKey)
        
        packet.asIPPacket().send(self.sock)
