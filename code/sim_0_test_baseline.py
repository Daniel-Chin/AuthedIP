"""
Test IP, which is our baseline. 

e: endhost, 
r: router, 
v: verifier, 
c: controller. 

e0 - r1 - r2 - e3
"""

from shared import *
from utils_for_sim import *
from router import *

def main():
    with InitRendezvous():
        e0 = Endhost()
        e0.ip_addr = Addr().random()
        r1 = Router()
        r2 = Router()
        e3 = Endhost()
        e3.ip_addr = Addr().random()

        serialConnect(e0, r1, r2, e3)
        r1.fillPortIds()
        r2.fillPortIds()

        installRoute(e0, r1, r2)
        installRoute(e3, r2, r1)

        interval = .01
        threads: List[LoopThread] = [
            ReadAloud(e0), 
            ReadAloud(e3), 
            r1, r2, 
            Babbler(e0, e3.ip_addr, interval), 
            Babbler(e3, e0.ip_addr, interval), 
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
