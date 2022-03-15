from shared import AuthedIpPacket, warn
from constants import SUBSCRIBE_INTERVAL

class VerifierServer:
    def __init__(self) -> None:
        self.known_authedip_routers = ...   # pre-configured

        self.known_public_keys = self.askControllerFor_known_public_keys()
        setInterval(SUBSCRIBE_INTERVAL, self.loop)
    
    def verify(
        self, packet : AuthedIpPacket, 
        router_ip,      # the router who duplicated the packet
        ingress_port,   # the ingress port of that router for the packet
    ):
        if not packet.verify(self.known_public_keys):
            warn(f'Bad packet: {packet}')
            self.sus(router_ip, ingress_port)
    
    def sus(self, router_ip, ingress_port):
        # Take note of the suspicious event
        (router_ip, ingress_port)
        # When evidence accumulates, tell the router to 
        # shut down that port. 
        return NotImplemented() / 0
    
    def askControllerFor_known_public_keys(self):
        # trivial
        return NotImplemented(
            'askControllerFor_known_public_keys'
        ) / 0
    
    def loop(self):
        # tell controller that I want to subscribe to:
        self.known_authedip_routers
        # If I'm being overloaded, however, partially unsubscribe. 

def setInterval(interval, func):
    # Just like in JavaScript. 
    # This conceptually starts to run `func` every `interval`. 
    # Realistically, start a thread. 
    return NotImplemented('setInterval', interval, func) / 0
