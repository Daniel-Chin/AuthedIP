from shared import *
from packet import *
from user import User

class Endhost:
    def __init__(self) -> None:
        self.ip_addr = ...

    def send(self, user : User, dest_addr, data):
        packet = AuthedIpPacket()
        packet.source_addr = self.ip_addr
        packet.dest_addr = dest_addr
        packet.content = data

        packet.rsa_public_key_id = user.rsa_public_key
        packet.signHash(user.rsa_private_key)
        
        self.ship(packet.asIPPacket())

    def ship(self, packet : IPPacket):
        # Ships a packet into the net. 
        return NotImplemented('ship', packet) / 0
