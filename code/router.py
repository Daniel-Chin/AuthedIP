from typing import List, Dict
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

        # isn't part of the protocol. is only in this demo. 
        self.peer = ...

class Router(LoopThread):
    def __init__(
        self, profile_volume = None, verbose=False, 
    ) -> None:
        super().__init__('router')

        self.profile_volume = profile_volume
        self.verbose = verbose

        self.ports: List[Port] = []
        self.table: Dict[bytes, Port] = {}
    
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
            payload_len = packet.parse(s)
            if self.profile_volume is not None:
                self.profile_volume.append(
                    payload_len + IP_HEADERS_LEN
                )
            self.forward(packet, in_port)
            # if self.verbose:
                # print(
                #     packet.source_addr, '->', packet.dest_addr, 
                # )

    def lookup(self, packet: IPPacket):
        try:
            out_port = self.table[packet.dest_addr.bytes]
        except KeyError:
            raise KeyError(f"""{
                packet.dest_addr
            } not in table of {self}.""")
        # if self.verbose:
            # print(packet.dest_addr, out_port.peer)
        return out_port

    def forward(self, packet: IPPacket, in_port: Port):
        out_port = self.lookup(packet)
        packet.send(out_port.sock)

class AuthedIPRouter(Router):
    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.ip_addr: Addr = ...
        self.controller_ip: Addr = ...    # pre-configured
        self.verifier_ip: Addr = None     
        # `verifier_ip` should be given by Controller; 
        # but in this demo, it's pre-configured. 
        self.port_sus = [0] * 99    # port.id -> sus
        self.last_time = time()
        self.side = None    # INSIDE | OUTSIDE
    
    def __repr__(self):
        return f'<Router {self.ip_addr}>'
    
    def checkProbability(self, sus):
        return BASE_CHECK_PROBABILITY * (1 + sus * .1)
    
    def noLeak(self, sus):
        return sus >= NO_LEAK_SUS

    def forward(self, packet: IPPacket, in_port: Port):
        if packet.dest_addr == self.ip_addr:
            # it's for me! 
            if in_port.side == INSIDE:
                self.readAlert(packet)
            else:
                self.port_sus[in_port.id] += 1
                warn('outside link sent packet to router')
        else:
            out_port = self.lookup(packet)
            sus = self.port_sus[in_port.id]
            if not self.noLeak(sus):
                # first, forward everything
                packet.send(out_port.sock)

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
                    ipPa = duPa.asIPPacket()
                    if self.noLeak(sus):
                        duPa.forward_this = b'1'
                    ipPa.send(
                        self.lookup(ipPa).sock, 
                    )
    
    def readAlert(self, packet: IPPacket):
        alPa = AlertPacket().fromIPPacket(packet)
        addr, port_id = alPa.ingress_info
        assert addr == self.ip_addr
        self.port_sus[port_id] += 1
        if (
            NO_LEAK_SUS - 1 < 
            self.port_sus[port_id] 
            <= NO_LEAK_SUS
        ):
            print(self, 'entered verify-then-forward mode.')

    def loop(self):
        # weighted round robin
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
