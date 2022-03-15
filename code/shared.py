from time import time

class IPPacket:
    def __init__(self) -> None:
        self.source_addr = None
        self.dest_addr = None
        self.payload = None

class AuthedIpPacket(IPPacket):
    def __init__(self) -> None:
        # Keeps everything from IP
        super().__init__()

        # AuthedIp
        self.content = None
        self.timestamp = str(time())
        self.hash = None
        self.rsa_public_key = None
        self.signature = None
    
    def hashContent(self):
        self.hash = str(hash((
            self.source_addr, 
            self.dest_addr, 
            self.content, 
        )))
    
    def signHash(self, rsa_private_key):
        self.signature = rsaSign(
            self.timestamp + self.hash, 
            rsa_private_key, 
        )
    
    def verify(self, known_public_keys):
        # Check if public key is registered
        if self.rsa_public_key not in known_public_keys:
            return False

        # Check RSA signature
        if not rsaVerify(
            self.timestamp + self.hash, 
            self.rsa_public_key, 
        ):
            return False
        
        # Check the hash
        if self.hash != str(hash((
            self.source_addr, 
            self.dest_addr, 
            self.content, 
        ))):
            return False
        
        # All OK
        return True
    
    def asIPPacket(self):
        p = IPPacket()
        p.source_addr = self.source_addr
        p.dest_addr   = self.dest_addr
        # The timestamp, hash, and the signature are embedded
        # within the payload of the IP packet. 
        p.payload = (   # Concatenation of four things
            self.timestamp + 
            self.hash + 
            self.rsa_public_key + 
            self.signature + 
            self.content
        )
        return p

def rsaSign(data, key):
    # The RSA signature function
    return NotImplemented(('rsaSign', data, key)) / 0

def rsaVerify(data, key):
    # The RSA signature verification function
    return NotImplemented(('rsaVerify', data, key)) / 0
