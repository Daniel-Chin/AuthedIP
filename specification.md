subscription
  has a rate limit
  router drops packets, looking like congestion for the hosts.

alarm should gradually raise the check probability. 

no more content verification
  since we only defend against dos. 
  content hash is optional, for those who to content security with network security. 

scream for help
  through Controller. 
  raise check probability for specific routers

limitations
  may need salting to prevent slow brute force of signature. Controller should declare salt of the day. 

registration
  RSA full key is 512 bits. Too long for every packet, so in the packet we only put the 8-byte suffix. This allows 256^8=1e+19 different accounts in the enterprise. 
  Generation of keys uses rejection sampling. 
