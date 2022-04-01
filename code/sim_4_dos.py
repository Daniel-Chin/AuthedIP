"""
DoS attack. 

e: endhost, 
r: router, 
v: verifier, 
c: controller. 

e0 - r1 - r6 - r2 - e3
     |         |
     v         r5
               |
               c
"""

from time import sleep

from shared import *
from utils_for_sim import *
from router import *
from controller import *
from verifier_server import *

def measure(
    is_authedip, for_how_long, 
):
    if is_authedip:
        SomeEndhost = AuthedIPEndhost
        SomeRouter = AuthedIPRouter
    else:
        SomeEndhost = Endhost
        SomeRouter = Router
    u0 = User().newKeys()
    u3 = User().newKeys()

    e0 = Endhost()
    e0.ip_addr = Addr(b'<e0>')
    e0.side = OUTSIDE
    e3 = SomeEndhost()
    e3.ip_addr = Addr(b'<e3>')
    e3.side = OUTSIDE

    c = Controller()
    c.ip_addr = Addr(b'<c >')
    c.known_public_keys = {
        u0.pubKeyId(): u0.pubKey, 
        u3.pubKeyId(): u3.pubKey, 
    }
    del c.sock

    v = VerifierServer()
    v.ip_addr = Addr(b'<v >')
    v.acquireKnownPublicKeys(c.known_public_keys)  # magic

    vols = {1: [], 2: [], 5: [], 6: []}
    r1 = SomeRouter(vols[1])
    r1.ip_addr = Addr(b'<r1>')
    r1.controller_ip = c.ip_addr
    r1.verifier_ip = v.ip_addr
    r1.side = INSIDE
    r2 = SomeRouter(vols[2])
    r2.ip_addr = Addr(b'<r2>')
    r2.controller_ip = c.ip_addr
    r2.verifier_ip = v.ip_addr
    r2.side = INSIDE
    r5 = SomeRouter(vols[5])
    r5.ip_addr = Addr(b'<r5>')
    r5.controller_ip = c.ip_addr
    r5.verifier_ip = v.ip_addr
    r5.side = INSIDE
    r6 = SomeRouter(vols[6])
    r6.ip_addr = Addr(b'<r6>')
    r6.controller_ip = c.ip_addr
    r6.verifier_ip = v.ip_addr
    r6.side = INSIDE

    serialConnect(e0, r1, r6, r2, e3)
    serialConnect(r1, v)
    serialConnect(r2, r5)
    r1.fillPortIds()
    r2.fillPortIds()
    r5.fillPortIds()
    r6.fillPortIds()

    installRoute(e0, r1, r6, r2, r5)
    installRoute(r1, r6, r2, r5)
    installRoute(r2, r5)
    installRoute(r2, r6, r1)
    installRoute(e3, r2, r6, r1)
    installRoute(e3, r2, r5)
    installRoute(r5, r2, r6, r1)
    installRoute(v, r1, r6, r2, r5)

    if not is_authedip:
        u0 = None
        u3 = None

    threads: List[LoopThread] = [
        Drain(e3), 
        r1, r2, r5, r6, v, 
        Babbler(
            e0, e3.ip_addr, 
            interval=0, user=None, bulk_data=True, # DoS
        ), 
    ]

    try:
        [x.start() for x in threads]
        sleep(for_how_long)
    finally:
        for thread in threads:
            thread.go_on = False
    
    return {k : sum(v) / 1024**2 for (k, v) in vols.items()}

def main():
    DURATION = 5
    with InitRendezvous():
        print(f'{DURATION=} seconds')
        print('measuring ip...')
        ip_vol = measure(False, DURATION)
        sleep(1.1)
        print('measuring authedip...')
        au_vol = measure(True , DURATION)
        sleep(1.1)
    print()
    overall_ip = 0
    overall_au = 0
    for k in (1, 2, 5, 6):
        overall_ip += ip_vol[k]
        overall_au += au_vol[k]
        try:
            ratio = format(au_vol[k] / ip_vol[k], '.1%')
        except ZeroDivisionError:
            ratio = 'NaN'
        print(
            f'r{k}\n', ' ', 
            '      ip volume:', format(ip_vol[k], '.3f'), 'MB', 
            'authedip volume:', format(au_vol[k], '.3f'), 'MB', 
            'ratio:', ratio, 
        )
    print('overall ratio:', format(
        overall_au / overall_ip, '.1%', 
    ))

main()
