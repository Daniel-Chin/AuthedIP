from os import urandom
from typing import List
from functools import lru_cache
from threading import Thread
from random import random
from time import time
from socket import socket
from select import select
import rsa
from shared import *
from constants import *
from packet import *
from endhost import Endhost, User

class Port:
    def __init__(self) -> None:
        self.sock : socket = None
        # which side is the peer on?
        self.side = None    # INSIDE | OUTSIDE

class Router(Thread):
    def __init__(self) -> None:
        super().__init__()
        self.ports : List[Port] = []
        self.table = {}
        self.go_on = True

    @lru_cache(1)
    def allSocks(self):
        return [x.sock for x in self.ports]
    
    @lru_cache()
    def sock2Port(self, sock : socket):
        for port in self.ports:
            if port.sock is sock:
                return port
    
    def run(self):
        while self.go_on:
            r_ready, _, _ = select(
                self.allSocks(), [], [], SHUTDOWN_TIME, 
            )
            for s in r_ready:
                s : socket
                in_port = self.sock2Port(s)
                packet = IPPacket()
                packet.parse(s)
                out_port = self.table[packet.dest_addr]
                self.forward(packet, in_port, out_port)
        print('router thread shutdown.')
    
    def forward(
        self, packet : IPPacket, 
        in_port : Port, out_port : Port, 
    ):
        packet.send(out_port.sock)

class AuthedIPRouter(Router, Endhost):
    def __init__(self) -> None:
        super().__init__()
        self.controller_rsa_public_key = ...    # pre-configured
        self.user : User = ...
        # pre-configured. Each router needs an RSA key pair. 

        self.verifier_ip = None     # given by Controller
        self.last_subscribe_time = None
    
    def forward(
        self, packet : IPPacket, 
        in_port : Port, out_port : Port, 
    ):
        # First forward everything
        super().forward(packet, in_port, out_port)

        # Sometimes wrap a duplicate of the packet
        # and send to verifier. 
        subscriber = self.subscriber()
        if subscriber is None:
            return  # no verifier is subscribing
        if not ingress_port.isFromOutside():
            # only check packets directly from the Outside
            return
        if random() < CHECK_PROBABILITY:
            self.send(
                self.user, 
                subscriber, 
                ingress_port + packet,  # concat
            )
            # This is `Endhost` method `send`! 
            # Which means, the wrapper is signed too. 
    
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
        noise = urandom(HASH_LEN)
        socket.send(noise)
        signed_noise = socket.recv(SIGNATURE_LEN)
        if not rsa.verify(
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
        ( action, verifier_ip ) = socket.recv()
        if action == SUBSCRIBE:
            self.verifier_ip = verifier_ip
            self.last_subscribe_time = time()
        elif action == UNSUBSCRIBE:
            self.verifier_ip = None
        socket.send(b'ok')
        socket.close()
