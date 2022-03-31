subscription
  duplicating has a rate limit specified during subscription
  router drops packets, looking like congestion for the hosts.

alert 
  should gradually raise the check probability. 
  at some point, becomes verify-then-forward. 

no more content verification
  since we only defend against dos. 
  content hash is optional, for those who to content security with network security. 

scream for help
  through Controller. 
  raise check probability for specific routers

limitations
  may need salting to prevent slow brute force of signature. Controller should declare salt of the day. 
  the conversation between router and verifier should be encrypted. or, check source IP. 
    otherwise, attacker can 
      send fake "duplicated packets" to verifier. The first ones will pass through. 
      send fake alerts to routers. 

registration
  RSA full key is 512 bits. Too long for every packet, so in the packet we only put the 8-byte suffix. This allows 256^8=1e+19 different accounts in the enterprise. 
  Generation of keys uses rejection sampling. 
