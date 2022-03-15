from os import urandom
from random import random
from time import time
from shared import IPPacket, rsaVerify, warn

CHECK_PROBABILITY = 0.1     # 10%
SUBSCRIBE_TIMEOUT = 60 * 5  # 5 mins

# constants
SUBSCRIBE = 'SUBSCRIBE'
UNSUBSCRIBE = 'UNSUBSCRIBE'

class Router:
    def forward(self, packet : IPPacket):
        outbound_port = self.lookup(packet.dest_addr)
        self.ship(packet, outbound_port)
    
    def lookup(ip_addr):
        # Just regular lookup table. 
        return NotImplemented('lookup', ip_addr) / 0

    def ship(self, packet : IPPacket, outbound_port):
        # Ships a packet to an outbound port. 
        return NotImplemented('ship', packet, outbound_port) / 0

class AuthedIPRouter(Router):
    def __init__(self) -> None:
        super().__init__()
        self.ip = None
        self.controller_rsa_public_key = None   # pre-configured

        self.verifier_ip = None     # given by Controller
        self.last_subscribe_time = None
    
    def forward(self, packet : IPPacket):
        # First forward everything
        super().forward(packet)

        # Sometimes wrap a duplicate of the packet
        # and send to verifier. 
        subscriber = self.subscriber()
        if subscriber is not None and random() < CHECK_PROBABILITY:
            wrapper = IPPacket()
            wrapper.source_addr = self.ip
            wrapper.dest_addr = subscriber
            wrapper.payload = packet
            super().forward(wrapper)
    
    def subscriber(self):
        if time() < self.last_subscribe_time + SUBSCRIBE_TIMEOUT:
            return self.verifier_ip
        else:
            return None

    def onAcceptTCP(self, socket):
        # Each AuthedIP router listens for TCP connections. 
        # Controller gives the router a TCP call to update
        # verifier subscription. 

        # Controller authenticates
        noise = urandom(256)
        socket.send(noise)
        signed_noise = socket.recv(256)
        if not rsaVerify(
            noise, signed_noise, 
            self.controller_rsa_public_key, 
        ):
            warn(
                'TCP connection from ... failed to '
                'authenticate as Controller. '
            )
            socket.close()
            return
        
        # parse command
        (action, verifier_ip) = socket.recv()
        if action == SUBSCRIBE:
            self.verifier_ip = verifier_ip
            self.last_subscribe_time = time()
        elif action == UNSUBSCRIBE:
            self.verifier_ip = None
        socket.send(b'ok')
        socket.close()
