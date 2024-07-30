'''
Helper library for robot stuff
'''
# pylint: disable=global-statement
import hashlib
import json
import select
import socket
import struct
import sys
import time

# Use this address and port for a UDP multicast group (note: this is not your ip address)
MULTICAST_GROUP_ADDR = '224.1.1.1'
MULTICAST_GROUP_PORT = 42069
multicast_group = (MULTICAST_GROUP_ADDR, MULTICAST_GROUP_PORT)
LAST_SIGN_TIME = 0

def create_tx_socket():
    '''
    Returns a socket object that's been setup for sending data
    '''
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # There's a timeout when reusing the same addr+port, we're going to disable it
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Multicast mode (TTL is 2 seconds)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    # Return socket for use
    return sock


def create_rx_socket():
    '''
    Returns a socket object that's been setup for receiving data
    '''
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Bind to the addr+port we'll be listening to
    sock.bind(multicast_group)

    # Create a membership struct and apply said membership to our socket
    mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP_ADDR), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Return socket for use
    return sock


def sock_has_data(sock):
    '''
    Checks if a socket has data that can be read on it
    '''
    readable, _writeable, _errored = select.select([sock], [], [], 0)
    return sock in readable

def _hash(secret, sign_time, payload):
    return hashlib.sha256((secret+str(sign_time)+payload).encode('utf8')).hexdigest()

def sock_recv_auth(sock, secret, time_threshold=1):
    '''
    Receives data with authentication
    time_threshold is an integer value in seconds (if the packet
    is older/newer than this, throw it away)
    '''
    global LAST_SIGN_TIME
    # Get some data
    packet = sock.recv(10240)

    # No packet - throw away packet
    if not packet:
        return None

    # We have a packet, calculate the time as soon as we received
    # the packet so we can compare times accurately
    time_now = time.time()

    # Try to decode packet json
    try:
        packet = json.loads(packet)

    # Bad json - throw away packet
    except json.decoder.JSONDecodeError as error:
        print('Bad packet json', file=sys.stderr)
        print(error, file=sys.stderr)
        return None

    # Grab the important bits
    payload = packet['payload']
    sign_time = packet['time']
    signature = packet['signature']

    # Calculate the signature on our side
    calculated_signature = _hash(secret, sign_time, payload)

    # Signature mismatch - throw away packet
    if calculated_signature != signature:
        print('Signature mismatch', file=sys.stderr)
        return None

    # Check if packet is too old
    if sign_time < time_now - time_threshold:
        print(f'Packet too old (sent {sign_time} received {time_now})', file=sys.stderr)
        return None

     # Check if packet is too new
    if sign_time > time_now + time_threshold:
        print(f'Packet too new (sent {sign_time} received {time_now})', file=sys.stderr)
        return None

    # Check if we've seen the packet before
    '''if sign_time <= LAST_SIGN_TIME:
        print(f'Packet seen before (sent {sign_time} received {time_now})', file=sys.stderr)
        return None'''

    LAST_SIGN_TIME = time_now

    # Try to decode json payload
    try:
        return json.loads(payload)

    # Bad payload - throw away
    except json.decoder.JSONDecodeError as error:
        print('Bad packet payload json', file=sys.stderr)
        print(error, file=sys.stderr)
        return None

def sock_send_auth(sock, secret, payload):
    '''
    Sends a payload with authentication
    '''
    # Turn payload into a string
    payload_data = json.dumps(payload)

    # Get the current sign time (now)
    sign_time = time.time()

    # Hash the secret + time + payload (aka the signature)
    signature =_hash(secret, sign_time, payload_data)

    # Make our packet and convert it to bytes
    packet = json.dumps({
        'payload': payload_data,
        'time': sign_time,
        'signature': signature
    }).encode('utf8')

    # Send packet
    sock.sendto(packet, multicast_group)
