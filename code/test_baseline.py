'''
e: endhost, 
r: router, 
v: verifier, 
c: controller. 

e0 - r1 - r2 - e3
'''

from shared import *
from utils_for_sim import *
from router import *

def main():
    e0 = Endhost()
    e0.ip_addr = Addr().random()
    r1 = Router()
    r2 = Router()
    e1 = Endhost()
    e1.ip_addr = Addr().random()

    e0.sock
    r1.ports
    r1.table

main()
