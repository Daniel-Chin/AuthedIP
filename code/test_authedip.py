"""
e: endhost, 
r: router, 
v: verifier, 
c: controller. 

e0 - r1 - r2 - e3
     |    |
     r4   r5
     |    |
     v    c
"""

from shared import *
from utils_for_sim import *
from router import *
from controller import *
from verifier_server import *

def main():
    with InitRendezvous():
        u0 = User().newKeys()
        u3 = User().newKeys()

        e0 = AuthedIPEndhost()
        e0.ip_addr = Addr().random()
        e0.side = OUTSIDE
        e3 = AuthedIPEndhost()
        e3.ip_addr = Addr().random()
        e3.side = OUTSIDE

        c = Controller()
        c.ip_addr = Addr().random()
        c.known_public_keys = {
            u0.pubKeyId(): u0.pubKey, 
            u3.pubKeyId(): u3.pubKey, 
        }
        del c.sock

        v = VerifierServer()
        v.ip_addr = Addr().random()
        v.acquireKnownPublicKeys(c.known_public_keys)  # magic

        r1 = AuthedIPRouter()
        r1.ip_addr = Addr(b'<r1>')
        r1.controller_ip = c.ip_addr
        r1.verifier_ip = v.ip_addr
        r1.side = INSIDE
        r2 = AuthedIPRouter()
        r2.ip_addr = Addr().random()
        r2.controller_ip = c.ip_addr
        r2.verifier_ip = v.ip_addr
        r2.side = INSIDE
        r4 = AuthedIPRouter()
        r4.ip_addr = Addr().random()
        r4.controller_ip = c.ip_addr
        r4.verifier_ip = v.ip_addr
        r4.side = INSIDE
        r5 = AuthedIPRouter()
        r5.ip_addr = Addr().random()
        r5.controller_ip = c.ip_addr
        r5.verifier_ip = v.ip_addr
        r5.side = INSIDE

        serialConnect(e0, r1, r2, e3)
        serialConnect(r1, r4, v)
        serialConnect(r2, r5)
        r1.fillPortIds()
        r2.fillPortIds()
        r4.fillPortIds()
        r5.fillPortIds()

        installRoute(e0, r1, r2, r5)
        installRoute(e0, r1, r4)
        installRoute(r1, r4)
        installRoute(r1, r2, r5)
        installRoute(r2, r5)
        installRoute(r2, r1, r4)
        installRoute(e3, r2, r1, r4)
        installRoute(e3, r2, r5)
        installRoute(r4, r1, r2, r5)
        installRoute(r5, r2, r1, r4)
        installRoute(v, r4, r1, r2, r5)
        # installRoute(c, r5, r2, r1, r4)

        interval = .1
        threads: List[LoopThread] = [
            ReadAloud(e0), 
            ReadAloud(e3), 
            r1, r2, r4, r5, v, 
            Babbler(e0, e3.ip_addr, interval, u0), 
            Babbler(e3, e0.ip_addr, interval, u3), 
        ]

        print('After starting, hit Enter to stop!')
        print()
        input('Hit Enter to start...')
        try:
            [x.start() for x in threads]
            print()
            print('Hit Enter to stop...')
            print()
            input()
        finally:
            for thread in threads:
                thread.go_on = False

main()
