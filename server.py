import queue
import sys
import socket
import constants
import struct
import asyncio
import time
import zlib


def safe_send(msg: str, sock: socket.socket, ADDR: (str, int)) -> None:
    msg = msg.encode(constants.ENCODING)
    sock.settimeout(1)
    packet_num = 0
    while True:
        packet_data = msg[packet_num * constants.PACKET_SIZE:(packet_num + 1) * constants.PACKET_SIZE]
        if not packet_data:
            break
        checksum = zlib.crc32(packet_data)
        packet = struct.pack('>I', packet_num) + struct.pack('>I', checksum) + packet_data

        ack_received = False
        while not ack_received:
            try:
                sock.sendto(packet, ADDR)
                ack, addr = sock.recvfrom(4)
                ack_num = struct.unpack('>I', ack)[0]
                if ack_num == packet_num:
                    # The receiver has acknowledged this packet
                    ack_received = True
            except socket.timeout:
                # The socket timed out waiting for an ACK message
                print(f"Packet {packet_num} timed out")

        # Move on to the next packet
        packet_num += 1


def safe_receive(sock: socket.socket) -> (str, (str, int)):
    pass


def main():
    IP = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8888

    print(f'ip: {IP}, port: {PORT}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))

    queues = dict()

    while True:
        data, addr = sock.recvfrom(constants.BUFFER_SIZE)
        data = data.decode(constants.ENCODING)
        name = data.split()[0]
        msg = data[len(name) + 1:]
        if msg:
            if name not in queues:
                queues[name] = queue.Queue(constants.QUEUE_MAX_SIZE)
            queues[name].put(msg)
            print(f'LOG: Got msg: {msg}')
        else:
            if name not in queues:
                print('ERROR: no such queue!')
                sock.sendto("ERROR: no such queue!".encode(constants.ENCODING), addr)
            else:
                if queues[name].empty():
                    queues.pop(name)
                    sock.sendto("Queue deleted".encode(constants.ENCODING), addr)
                else:
                    sock.sendto(queues[name].get().encode(constants.ENCODING), addr)


if __name__ == '__main__':
    main()
