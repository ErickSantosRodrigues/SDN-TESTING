import socket
import struct


def send_dns_query(server, name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0))
    sock.settimeout(2)
    
    # Generate a simple query message
    query = struct.pack('>H', 1)  # Query ID
    query += b'\x01\x00'  # Flags
    query += b'\x00\x01'  # Questions
    query += b'\x00\x00'  # Answer RRs
    query += b'\x00\x00'  # Authority RRs
    query += b'\x00\x00'  # Additional RRs
    for part in name.split('.'):
        query += struct.pack('B', len(part)) + part.encode('utf-8')
    query += b'\x00'  # End of name
    query += b'\x00\x01'  # Type: A
    query += b'\x00\x01'  # Class: IN
    
    sock.sendto(query, server)


send_dns_query(('10.0.0.1', 53), 'google.com')

