ENDIAN = 'big'

class Addr:
    def __init__(self, addr_bytes = None) -> None:
        self.bytes = addr_bytes
    
    def __repr__(self):
        return '.'.join([str(x) for x in self.bytes])

def warn(message):
    print(message)
    # And also log it to a file, notify operator, etc. 

def recvall(s, size, use_list = True):
    '''
    Receive `size` bytes from socket `s`. Blocks until gets all. 
    Somehow doesn't handle socket closing. 
    I will fix that when I have time. 
    '''
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
