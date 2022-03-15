# Global synchronization of BBR cycles

Daniel Chin, nq285

## Motivation
When BBR does congestion control, they need to synchronize with other end hosts to modulate the queue length in gateways. Ideally, the globe should pulsate as a whole. However, It takes multiple milliseconds for light to travel around the globe. How can BBR synchronize its probing cycles on the global scale? 

I did a preliminary experiment of self-synchronization under finite lightspeed on (1) a sphere and (2) a torus: [https://github.com/Daniel-Chin/self-sync-w-finite-light-speed-and-closed-boundary#self-synchronization-with-locality-and-closed-boundaries](https://github.com/Daniel-Chin/self-sync-w-finite-light-speed-and-closed-boundary#self-synchronization-with-locality-and-closed-boundaries). I expected to see wave patterns traveling at lightspeed, and I expected the torus to have better stability than the sphere, because I couldn't imagine any stable wave pattern on a sphere surface. However, the experiment showed that the sphere was actually more stable. The wave patterns on the sphere was hard to describe and evolved with time, but there was clearly an attractor. 

## Problem Statement
With this semester's project, I intend to investigate this self-synchronization under finite lightspeed on the sphere surface. Specifically,  
- How many stable patterns are there? Can I classify them? 
- What are the attractors? i.e. what are the trajectories of those stable patterns? 
- What initial conditions are prone to form stable patterns? 
- How stable are they? How much noise can they take? 
- Practically, what it means for the design of BBR. 

## Timeline
- Mar. Pilot experiments; automatic pattern summarization. 
- Apr. Mass auto-managed experiments; data inspection; presentations. 

## One Experiment with Hypothesis for the project
Experiment: mentioned above.  
Hypothesis: I expect to see only one attractor. 

Feb. 13, 2022. 
