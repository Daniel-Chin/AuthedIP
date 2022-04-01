ENDIAN = 'big'

import os
from time import time
from socket import socket, timeout as SocketTimeout
from threading import Thread, Lock
import traceback

from constants import *

class Addr:
    def __init__(self, addr_bytes = None) -> None:
        self.bytes = addr_bytes
    
    def __repr__(self):
        nums = '.'.join([format(x, '3') for x in self.bytes])
        return f'[{self.bytes} {nums}]'
    
    def random(self):
        self.bytes = os.urandom(4)
        print(self)
        return self
    
    def __eq__(self, other):
        return self.bytes == other.bytes

def warn(message):
    print('WARNING:', message)
    # And also log it to a file, notify operator, etc. 

def recvall(s: socket, size: int, timeout=5, dt=1):
    """
    Receive `size` bytes from socket `s`.  
    `timeout` is in seconds. If `None`, blocks until gets all. 
    Somehow doesn't handle socket closing. 
    I will fix that when I have time. 
    """
    left = size
    buffer = []
    if timeout is None:
        s.settimeout(None)
    else:
        deadline = time() + timeout
        s.settimeout(dt)
    while left > 0:
        try:
            recved = s.recv(left)
        except SocketTimeout:
            pass
        if recved == b'':
            raise EOFError(f'Socket {s} remote closed. ')
        buffer.append(recved)
        left -= len(recved)
        if (
            timeout is not None 
            and time() > deadline 
            and left > 0
        ):
            raise TimeoutError
    return b''.join(buffer)

stackTraceLock = Lock()
class LoopThread(Thread):
    def __init__(self, name=None) -> None:
        super().__init__(name=name)
        self.go_on = True
    
    def run(self):
        try:
            while self.go_on:
                self.loop()
        except:
            with stackTraceLock:
                print(f'LoopThread {self.name} exception:')
                traceback.print_exc()
                print()
        finally:
            print(f'LoopThread {self.name} shutdown.')
