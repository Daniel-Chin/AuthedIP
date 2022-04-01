from os import urandom
from time import sleep, perf_counter
from socket import socket
from select import select

from shared import *
from net_interface import *
from router import *

RENDEZVOUS = ( 'localhost', 2333 )
Endhost = NetInterface
AuthedIPEndhost = AuthedIPNetInterface

serverSock: socket = None

class InitRendezvous():
    def __enter__(self):
        global serverSock
        assert serverSock is None
        serverSock = socket()
        serverSock.bind(RENDEZVOUS)
        serverSock.listen(16)
    
    def __exit__(self, *_):
        serverSock.close()
        return False

def newLink():
    s0 = socket()
    s0.connect(RENDEZVOUS)
    s1, (ip_addr, _) = serverSock.accept()
    assert ip_addr in (RENDEZVOUS[0], '127.0.0.1')
    return s0, s1

def serialConnect(*nodes):
    for n0, n1 in zip(nodes[:-1], nodes[1:]):
        for node, sock, peer in zip(
            (n0, n1), newLink(), (n1, n0), 
        ):
            try:
                node.sock
            except AttributeError:
                port = Port()
                port.sock = sock
                try:
                    port.side = peer.side
                except AttributeError:
                    port.side = None
                port.peer = peer    # demo-only
                node.ports.append(port)
            else:
                node.sock = sock

def installRoute(*nodes):
    dest = nodes[0]
    for left_node, right_node in zip(nodes[:-1], nodes[1:]):
        right_node: Router
        right_node.table[dest.ip_addr.bytes] = [
            x for x in right_node.ports 
            if x.peer is left_node
        ][0]

class ReadAloud(LoopThread):
    def __init__(self, endhost: Endhost) -> None:
        super().__init__()

        self.endhost = endhost
    
    def loop(self):
        r_ready, _, _ = select(
            [self.endhost.sock], [], [], 
            SHUTDOWN_TIME, 
        )
        if r_ready:
            ipPa = IPPacket()
            ipPa.parse(r_ready[0])
            print(self.endhost, self.endhost.unbox(ipPa))

class StoreLatency(LoopThread):
    def __init__(self, endhost: Endhost, storage) -> None:
        super().__init__()

        self.endhost = endhost
        self.storage = storage
    
    def loop(self):
        r_ready, _, _ = select(
            [self.endhost.sock], [], [], 
            SHUTDOWN_TIME, 
        )
        if r_ready:
            ipPa = IPPacket()
            ipPa.parse(r_ready[0])
            dt = perf_counter() - float(
                self.endhost.unbox(ipPa)[1].split(b'\n', 1)[0],
            )
            self.storage.append(dt)

class Babbler(LoopThread):
    def __init__(
        self, endhost: Endhost, to_who: Addr, 
        interval = 1, user = None, bulk_data = False, 
    ) -> None:
        super().__init__()

        self.endhost = endhost
        self.to_who: Addr = to_who
        self.interval = interval
        self.bulk_data = bulk_data
        self.send_kw = {}
        if user is not None:
            self.send_kw['user'] = user
    
    def loop(self):
        content = str(perf_counter()).encode()
        if self.bulk_data:
            content += b'\n' + urandom(256)
        self.endhost.send(
            self.to_who, 
            content, 
            **self.send_kw, 
        )
        sleep(self.interval)
