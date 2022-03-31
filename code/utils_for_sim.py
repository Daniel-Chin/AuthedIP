from time import sleep
from socket import socket
from select import select
from shared import *
from net_interface import *

RENDEZVOUS = ( 'localhost', 2333 )
Endhost = NetInterface

serverSock: socket = None

def init():
    global serverSock
    serverSock = socket()
    serverSock.bind(RENDEZVOUS)
    serverSock.listen(16)
init()

def newLink():
    s0 = socket()
    s0.connect(RENDEZVOUS)
    s1, (ip_addr, _) = serverSock.accept()
    assert ip_addr in (RENDEZVOUS[0], '127.0.0.1')
    return s0, s1

def serialConnect(*nodes):
    last_node = nodes[0]
    for node in nodes[1:]:
        ...

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
