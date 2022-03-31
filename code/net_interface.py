from socket import socket
from shared import *
from packet import *
from user import User

class NetInterface:
    def __init__(self) -> None:
        self.ip_addr = ...

        # represents physical link
        self.sock: socket = ...

    def send(self, dest_addr, data):
        packet = IPPacket()
        packet.source_addr = self.ip_addr
        packet.  dest_addr = dest_addr
        packet.payload = data
        packet.send(self.sock)

class AuthedIPNetInterface(NetInterface):
    def send(self, dest_addr, data, user: User):
        packet = AuthedIpPacket()
        packet.source_addr = self.ip_addr
        packet.  dest_addr = dest_addr
        packet.content = data

        packet.rsa_public_key_id = user.pubKeyId()
        packet.sign(user.priKey)
        
        packet.asIPPacket().send(self.sock)
