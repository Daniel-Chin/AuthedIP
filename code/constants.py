PACKET_TIMEOUT = 10     # 10 s
BASE_CHECK_PROBABILITY = 0.1     # 10%
SUS_DECAY = .05   # sus per second
NO_LEAK_SUS = 4

ENDIAN = 'big'
RSA_KEY_BITS = 512
HASH_METHOD = 'SHA-256'
HASH_LEN = 32
IP_ADDR_LEN = 4
PORT_ID_LEN = 1
IP_HEADERS_LEN = 2 + 2 + 8 + 4 + 4
assert IP_HEADERS_LEN == 20
TIMESTAMP_LEN = 16
RSA_KEY_ID_BITS = 64
SIGNATURE_LEN = 64
INGRESS_INFO_LEN = IP_ADDR_LEN + PORT_ID_LEN

SUBSCRIBE = 'SUBSCRIBE'
UNSUBSCRIBE = 'UNSUBSCRIBE'
INSIDE = 'INSIDE'
OUTSIDE = 'OUTSIDE'

SHUTDOWN_TIME = 3
