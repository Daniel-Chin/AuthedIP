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

from time import sleep

from matplotlib import pyplot as plt

from shared import *
from utils_for_sim import *
from router import *
from controller import *
from verifier_server import *

def measure(is_authedip, for_how_long, interval):
    if is_authedip:
        SomeEndhost = AuthedIPEndhost
        SomeRouter = AuthedIPRouter
    else:
        SomeEndhost = Endhost
        SomeRouter = Router
    u0 = User().newKeys()
    u3 = User().newKeys()

    e0 = SomeEndhost()
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

    r1 = SomeRouter()
    r1.ip_addr = Addr(b'<r1>')
    r1.controller_ip = c.ip_addr
    r1.verifier_ip = v.ip_addr
    r1.side = INSIDE
    r2 = SomeRouter()
    r2.ip_addr = Addr(b'<r2>')
    r2.controller_ip = c.ip_addr
    r2.verifier_ip = v.ip_addr
    r2.side = INSIDE
    r4 = SomeRouter()
    r4.ip_addr = Addr(b'<r4>')
    r4.controller_ip = c.ip_addr
    r4.verifier_ip = v.ip_addr
    r4.side = INSIDE
    r5 = SomeRouter()
    r5.ip_addr = Addr(b'<r5>')
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

    if not is_authedip:
        u0 = None
        u3 = None

    latencies = []
    threads: List[LoopThread] = [
        StoreLatency(e0, latencies), 
        StoreLatency(e3, latencies), 
        r1, r2, r4, r5, v, 
        Babbler(e0, e3.ip_addr, interval, u0), 
        Babbler(e3, e0.ip_addr, interval, u3), 
    ]

    try:
        [x.start() for x in threads]
        sleep(for_how_long)
        latencies = latencies[:]    # avoids post-stop data
    finally:
        for thread in threads:
            thread.go_on = False
    
    return latencies

def main():
    DURATION = 5
    interval = .02
    with InitRendezvous():
        # print('warming up...')
        # measure(False, 1)
        # sleep(1.1)
        print(f'{DURATION=} seconds')
        print('measuring ip...')
        ip       = measure(False, DURATION, interval)
        sleep(1.1)
        print('measuring authedip...')
        authedip = measure(True , DURATION, interval)
    print('sample size:', len(ip), len(authedip))
    CUTOFF = .01
    ip       = [x * 1000 for x in ip       if x < CUTOFF]
    authedip = [x * 1000 for x in authedip if x < CUTOFF]
    merged = sorted(ip + authedip)
    min_, max_ = merged[1], merged[-2]
    params = {
        'bins': round((max_ - min_) / .1), 
        'range': (min_, max_), 
        # 'density': True, 
    }
    plt.hist(
        authedip, fc=(0, 0, 1, .5), label='authedip', 
        **params, 
    )
    plt.hist(
        ip,       fc=(1, 0, 0, .5), label='ip', 
        **params, 
    )
    plt.legend()
    plt.xlabel('Latency (ms)')
    plt.ylabel('Frequency')
    plt.show()

main()
