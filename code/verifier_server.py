from socket import socket
from select import select
from shared import *
from packet import *

class VerifierServer(LoopThread):
    def __init__(self) -> None:
        super().__init__()

        self.ip_addr: Addr = ...
        self.known_public_keys = None
        # represents physical link
        self.sock: socket = ...
    
    def acquireKnownPublicKeys(self, pre_configured):
        # verifier is supposed to ask controller for this. 
        # But this is very trivial.
        # In this demo, known_public_keys is preconfigured. 
        self.known_public_keys = pre_configured
    
    def loop(self):
        r_ready, _, _ = select([self.sock], [], [], SHUTDOWN_TIME)
        if not r_ready:
            return
        ipPa = IPPacket()
        ipPa.parse(r_ready[0], stop_before_payload=True)
        ipPa.payload = b''
        duPa = DuplicatedPacket().fromIPPacket(ipPa)
        router_ip, _ = duPa.ingress_info
        inner = IPPacket()
        inner.parse(r_ready[0])
        auPa = AuthedIpPacket().fromIPPacket(inner)
        
        if auPa.verify(self.known_public_keys):
            if duPa.forward_this:
                inner.send(self.sock)
        else:
            warn(f'Bad packet: {auPa}')
            alPa = AlertPacket()
            alPa.source_addr = self.ip_addr
            alPa.  dest_addr = router_ip
            alPa.ingress_info = duPa.ingress_info
            alPa.asIPPacket().send(self.sock)
