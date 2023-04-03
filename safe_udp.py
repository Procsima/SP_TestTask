import socket
import constants
import hashlib
import struct


def send(msg: str, sock: socket.socket, ADDR: (str, int)) -> None:
    msg = msg.encode(constants.ENCODING)
    sock.settimeout(constants.PACKET_TIMEOUT)
    packet_num = 0

    size = len(msg)

    while True:
        packet_data = msg[packet_num * constants.MESSAGE_SIZE:(packet_num + 1) * constants.MESSAGE_SIZE]
        if not packet_data:
            break
        packet_data = struct.pack('>I', size) + packet_data
        checksum = hashlib.md5(packet_data).digest()
        packet = struct.pack('>I', packet_num) + struct.pack('16B', *checksum) + packet_data

        ack_received = False
        while not ack_received:
            try:
                sock.sendto(packet, ADDR)
                ack, addr = sock.recvfrom(4)
                ack_num = struct.unpack('>I', ack)[0]
                if ack_num == packet_num:
                    ack_received = True
            except socket.timeout:
                print(f"Packet {packet_num} timed out")

        packet_num += 1

    sock.settimeout(None)


def receive(sock: socket.socket) -> (str, (str, int)):
    msg = b''
    f = True
    best_addr = ('', 0)
    exp_packet_num = 0
    while True:
        packet = ''
        try:
            packet, addr = sock.recvfrom(constants.PACKET_SIZE)
            if f:
                best_addr = addr
                f = False
            if best_addr != addr:
                continue
        except socket.timeout:
            return '', addr
        # print(packet, len(packet))
        packet_num = struct.unpack('>I', packet[:4])[0]
        checksum = bytes(struct.unpack('16B', packet[4:20]))
        size = struct.unpack('>I', packet[20:24])[0]
        packet_data = packet[24:]

        if hashlib.md5(packet[20:]).digest() != checksum:
            print(f"Packet {packet_num} checksum mismatch")
            continue

        if exp_packet_num == packet_num:
            msg += packet_data
            if packet_num == 0:
                sock.settimeout(constants.CLIENT_TIMEOUT)
            # if packet_num == 2 and f: # making fake lag
            #     exp_packet_num += 1
            #     f = False
            #     continue
            sock.sendto(struct.pack('>I', exp_packet_num), addr)
            exp_packet_num += 1
        else:
            sock.sendto(struct.pack('>I', exp_packet_num - 1), addr)
            print(f'Resent packet number {packet_num}')

        if len(msg) >= size:
            break
    sock.settimeout(None)
    return msg.decode(constants.ENCODING), addr
