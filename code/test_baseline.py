"""
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

        installRoute(e0, r1, r2)
        installRoute(e3, r2, r1)

        threads: List[LoopThread] = [
            ReadAloud(e0), 
            ReadAloud(e3), 
            r1, r2, 
            Babbler(e0), 
            Babbler(e3), 
        ]
        [x.start() for x in threads]

        input('Enter to quit...')

        for thread in threads:
            thread.go_on = False

main()
