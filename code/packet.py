from functools import lru_cache
from typing import Tuple
from time import time
import rsa
from shared import *

class BasePacket:
    def __init__(self) -> None:
        self.source_addr: Addr = None
        self.  dest_addr: Addr = None

class IPPacket(BasePacket):
    def __init__(self) -> None:
        super().__init__()
        self.payload: bytes = None

        self.buffer = []
    
    def send(self, io):
        # version, IHL
        io.send(((4 << 4) + 5).to_bytes(1, ENDIAN))
        # DSCP, ECN
        io.send(b'\x00')
        # Total len
        io.send((IP_HEADERS_LEN + len(self.payload)).to_bytes(2, ENDIAN))
        # identification, flags, frag offset
        io.send(b'\x00\x00\x00\x00')
        # TTL, protocol, header checksum
        io.send(b'\x20\x00\x00\x00')
        # addr
        io.send(self.source_addr.bytes)
        io.send(self.dest_addr.bytes)
        # no options
        pass
        # payload
        io.send(self.payload)
    
    def recvAll(self, sock, size):
        data = recvall(sock, size)
        self.buffer.append(data)
        return data

    def parse(self, io, stop_before_payload = False):
        self.recvall(io, 2)
        payload_len = int.from_bytes(
            self.recvall(io, 2), ENDIAN, 
        ) - IP_HEADERS_LEN
        self.recvall(io, 8)
        self.source_addr = Addr(self.recvall(io, 4))
        self.  dest_addr = Addr(self.recvall(io, 4))
        if not stop_before_payload:
            self.payload = self.recvall(io, payload_len)
        return payload_len
    
    @lru_cache(1)
    def bytes(self):
        return b''.join(self.buffer)

class AuthedIpPacket(BasePacket):
    def __init__(self) -> None:
        super().__init__()

        # AuthedIp
        self.content: bytes = None
        self.timestamp: int = round(time())
        self.rsa_public_key_id: bytes = None
        self.signature: bytes = None
    
    def timestampBytes(self):
        return self.timestamp.to_bytes(TIMESTAMP_LEN, ENDIAN)

    def identity(self):
        return (
            self.timestampBytes() + 
            self.source_addr.bytes + 
            self.  dest_addr.bytes
        )

    def sign(self, rsa_private_key):
        self.signature = rsa.sign(
            self.identity(), rsa_private_key, HASH_METHOD, 
        )
    
    def verify(self, known_public_keys):
        # Check if fresh
        if time() - self.timestamp >= PACKET_TIMEOUT:
            return False
        
        # Check if public key is registered
        try:
            rsa_public_key = known_public_keys[self.rsa_public_key_id]
        except KeyError:
            return False

        # Check RSA signature
        try:
            if rsa.verify(
                self.identity(), self.signature, 
                rsa_public_key, 
            ) != HASH_METHOD:
                raise ValueError
        except (ValueError, rsa.pkcs1.VerificationError):
            return False
        
        # All OK
        return True
    
    def asIPPacket(self):
        p = IPPacket()
        p.source_addr = self.source_addr
        p.dest_addr   = self.dest_addr
        # The timestamp, key_id, and the signature are embedded
        # within the payload of the IP packet. 
        p.payload = (   # Concatenation of four things
            self.timestampBytes() + 
            self.rsa_public_key_id + 
            self.signature + 
            self.content
        )
        return p
    
    def fromIPPacket(self, packet: IPPacket):
        self.source_addr = packet.source_addr
        self.  dest_addr = packet.  dest_addr
        acc = 0
        self.timestamp = int.from_bytes(packet.payload[
            acc:acc+TIMESTAMP_LEN
        ], ENDIAN)
        acc += TIMESTAMP_LEN
        self.rsa_public_key_id = packet.payload[
            acc:acc+RSA_KEY_ID_BITS
        ]
        acc += RSA_KEY_ID_BITS
        self.signature = packet.payload[
            acc:acc+SIGNATURE_LEN
        ]
        acc += SIGNATURE_LEN
        self.content = packet.payload[acc:]
        return self

class DuplicatedPacket(BasePacket):
    def __init__(self) -> None:
        super().__init__()
        self.ingress_info: Tuple[Addr, int] = None     
        self.forward_this = b'0'    # b'0' | b'1'
        # (addr, port.id)
        self.content: bytes = None

    def ingressInfoBytes(self):
        addr , port_id = self.ingress_info
        return (
            addr.bytes + 
            port_id.to_bytes(PORT_ID_LEN, ENDIAN)
        )

    def asIPPacket(self):
        p = IPPacket()
        p.source_addr = self.source_addr
        p.dest_addr   = self.dest_addr
        p.payload = (
            self.ingressInfoBytes() + 
            self.forward_this + 
            self.content
        )
        return p

    def fromIPPacket(self, packet: IPPacket):
        self.source_addr = packet.source_addr
        self.  dest_addr = packet.  dest_addr
        acc = 0
        addr, port_id_enc = packet.payload[
            acc:acc+INGRESS_INFO_LEN
        ]
        self.ingress_info = (
            addr, int.from_bytes(port_id_enc, ENDIAN), 
        )
        acc += INGRESS_INFO_LEN
        self.forward_this = packet.payload[
            acc:acc+1
        ]
        acc += 1
        self.content = packet.payload[acc:]
        return self

class AlertPacket(DuplicatedPacket):
    def __init__(self) -> None:
        super().__init__()
        self.content = b''
