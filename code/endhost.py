from shared import IPPacket, AuthedIpPacket

class User:
    def __init__(self) -> None:
        # The RSA public key is registered with the Controller. 
        self.rsa_public_key = ...
        self.rsa_private_key = ...

class Endhost:
    def __init__(self) -> None:
        self.ip_addr = ...

    def send(self, user : User, dest_addr, data):
        packet = AuthedIpPacket()
        packet.source_addr = self.ip_addr
        packet.dest_addr = dest_addr
        packet.content = data

        packet.hashContent()
        packet.rsa_public_key = user.rsa_public_key
        packet.signHash(user.rsa_private_key)
        
        self.ship(packet.asIPPacket())

    def ship(self, packet : IPPacket):
        # Ships a packet into the net. 
        return NotImplemented('ship', packet) / 0
