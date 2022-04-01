"""
How much network throughput per verifier CPU power? 

My processor is 8-core @ 3GHz: 
    11th Gen Intel(R) Core(TM) i7-1185G7 @ 3.00GHz   3.00 GHz

I'm using single thread. 
Results:
    time per packet: 0.0369 ms
    packets per second: 27106.779568210688

    Assuming CHECK_PROBABILITY = 10%, 
    effective throughput is 271068 packets per second. 
    Assuming 60000 bytes per packet, 
    we have 15.1 GB/s per laptop CPU core in Python. 
"""

N_USERS = 1000
N_PACKETS = 10000

import random
from time import perf_counter
from typing import List
# from multiprocessing import Pool

from cacheWithFile import cacheWithFile
from jdt import jdtIter
from user import *
from packet import *

@cacheWithFile('users')
def genUsers():
    print(f'Generating {N_USERS} users...')
    users = []
    for _ in jdtIter(range(N_USERS), goal=N_USERS, UPP=8):
        users.append(User().newKeys())
    return users

def main():
    users = genUsers()
    print('Registering users...')
    known_keys = {}
    for user in jdtIter(users, UPP=16):
        assert user.pubKeyId() not in known_keys
        # Failing this assert has probability ~= 0. 
        # In reality you should use Rejection Sampling. 
        known_keys[user.pubKeyId()] = user.pubKey
    print(f'Generating {N_PACKETS} packets...')
    packets: List[IPPacket] = []
    for _ in jdtIter(range(N_PACKETS), goal=N_PACKETS, UPP=64):
        packet = AuthedIpPacket()
        packet.source_addr = Addr().random(verbose=False)
        packet.  dest_addr = Addr().random(verbose=False)
        packet.content = b''    
        # The content is not verified, so takes no time
        user = random.choice(users)
        packet.rsa_public_key_id = user.pubKeyId()
        packet.timestamp += 9999
        packet.sign(user.priKey)
        packets.append(packet.asIPPacket())
    print('Verifying...')
    # def verify(ipPa: IPPacket):
    #     AuthedIpPacket().fromIPPacket(ipPa).verify(known_keys)
    start = perf_counter()
    # with Pool(processes=8) as pool:
    #     pool.map(verify, packets)
    for ipPa in packets:
        AuthedIpPacket().fromIPPacket(ipPa).verify(known_keys)
    t = perf_counter() - start
    tpp = t / N_PACKETS
    print('time per packet:', format(tpp * 1000, '.4f'), 'ms')
    print('packets per second:', 1 / tpp)

main()
