ENDIAN = 'big'

import os
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

def recvall(s, size, use_list = True):
    """
    Receive `size` bytes from socket `s`. Blocks until gets all. 
    Somehow doesn't handle socket closing. 
    I will fix that when I have time. 
    """
    if use_list:
        left = size
        buffer = []
        while left > 0:
            buffer.append(s.recv(left))
            left -= len(buffer[-1])
        recved = b''.join(buffer)
    else:
        recved = b''
        while len(recved) < size:
            recved += s.recv(left)
    return recved

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
