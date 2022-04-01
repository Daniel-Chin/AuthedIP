from typing import List
from functools import lru_cache
from random import random
from time import time
from socket import socket
from select import select

from shared import *
from packet import *

class Port:
    def __init__(self) -> None:
        self.id = None
        self.sock: socket = None
        # which side is the peer on?
        self.side = None    # INSIDE | OUTSIDE
        # demo-only
        self.peer = ...

class Router(LoopThread):
    def __init__(self) -> None:
        super().__init__()

        self.ports: List[Port] = []
        self.table = {}
    
    def fillPortIds(self):
        for i, port in enumerate(self.ports):
            port.id = i

    @lru_cache(1)
    def allSocks(self):
        return [x.sock for x in self.ports]
    
    @lru_cache()
    def sock2Port(self, sock: socket):
        for port in self.ports:
            if port.sock is sock:
                return port
    
    def loop(self):
        r_ready, _, _ = select(
            self.allSocks(), [], [], SHUTDOWN_TIME, 
        )
        for s in r_ready:
            s: socket
            in_port = self.sock2Port(s)
            packet = IPPacket()
            packet.parse(s)
            self.forward(packet, in_port)

    def forward(self, packet: IPPacket, in_port: Port):
        try:
            out_port = self.table[packet.dest_addr.bytes]
        except KeyError:
            raise KeyError(f"""{
                packet.dest_addr
            } not in table of {self}.""")
        packet.send(out_port.sock)
        return out_port

class AuthedIPRouter(Router):
    def __init__(self) -> None:
        super().__init__()
        self.ip_addr: Addr = ...
        self.controller_ip: Addr = ...    # pre-configured
        self.verifier_ip: Addr = None     
        # `verifier_ip` should be given by Controller; 
        # but in this simulation, it's pre-configured. 
        self.port_sus = [0] * 99    # port.id -> sus
        self.last_time = time()
        self.side = None    # INSIDE | OUTSIDE
    
    def __repr__(self):
        return f'<Router {self.ip_addr}>'
    
    def checkProbability(self, sus):
        return BASE_CHECK_PROBABILITY * (1 + sus * .1)
    
    def noLeak(self, sus):
        return sus >= 4

    def forward(self, packet: IPPacket, in_port: Port):
        if packet.dest_addr == self.ip_addr:
            # it's for me! 
            if in_port.side == INSIDE:
                self.readAlert(packet)
            else:
                self.port_sus[in_port.id] += 1
                warn('outside link sent packet to router')
        else:
            sus = self.port_sus[in_port.id]
            if not self.noLeak(sus):
                # first, forward everything
                out_port = super().forward(packet, in_port)

            # Sometimes wrap a duplicate of the packet
            # and send to verifier. 
            if in_port.side == OUTSIDE and out_port.side == INSIDE:
                if (
                    self.noLeak(sus) 
                    or random() < self.checkProbability(sus)
                ):
                    duPa = DuplicatedPacket()
                    duPa.content = packet.bytes()
                    duPa.source_addr = self.ip_addr
                    duPa.  dest_addr = self.verifier_ip
                    duPa.ingress_info = (self.ip_addr, in_port.id)
                    if self.noLeak(sus):
                        duPa.forward_this = True
                    super().forward(duPa.asIPPacket(), None)
    
    def readAlert(self, packet: IPPacket):
        alPa = AlertPacket().fromIPPacket(packet)
        addr, port_id = alPa.ingress_info
        assert addr == self.ip_addr
        self.port_sus[port_id] += 1

    def loop(self):
        for _ in range(16):
            if not self.go_on:
                break
            super().loop()
        self.decaySus()
    
    def decaySus(self):
        dt = time() - self.last_time
        self.last_time += dt
        for port in self.ports:
            self.port_sus[port.id] = max(
                0, self.port_sus[port.id] - dt * SUS_DECAY, 
            )
