from time import sleep
from socket import socket
from select import select

from shared import *
from net_interface import *
from router import *

RENDEZVOUS = ( 'localhost', 2333 )
Endhost = NetInterface

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
    for node_pair in zip(nodes[1:], nodes[:-1]):
        for node, sock, peer in zip(
            node_pair, newLink(), reversed(node_pair), 
        ):
            try:
                node.sock
            except AttributeError:
                port = Port()
                port.sock = sock
                port.side = peer.side
                port.peer = peer    # demo-only
                node.ports.append(port)
            else:
                node.sock = sock

def installRoute(*nodes):
    dest = nodes[0]
    for left_node, right_node in zip(nodes[1:], nodes[:-1]):
        right_node: Router
        right_node.table[dest.ip_addr] = [
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
            print(self.endhost.ip_addr, 'got:', ipPa.payload)

class Babbler(LoopThread):
    def __init__(
        self, endhost: Endhost, to_who: Addr, 
        interval = 1, 
    ) -> None:
        super().__init__()

        self.endhost = endhost
        self.to_who: Addr = to_who
        self.interval = interval
    
    def loop(self):
        self.endhost.send(
            self.to_who, 
            b'This is a test message. ', 
        )
        sleep(self.interval)
