import socket
import constants
import zlib
import struct


def send(msg: str, sock: socket.socket, ADDR: (str, int)) -> None:
    msg = msg.encode(constants.ENCODING)
    sock.settimeout(constants.TIMEOUT)
    packet_num = 0

    size = len(msg)

    while True:
        packet_data = msg[packet_num * constants.MESSAGE_SIZE:(packet_num + 1) * constants.MESSAGE_SIZE]
        if not packet_data:
            break
        packet_data = struct.pack('>I', size) + packet_data
        checksum = zlib.crc32(packet_data)
        packet = struct.pack('>I', packet_num) + struct.pack('>I', checksum) + packet_data

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
    exp_packet_num = 0
    while True:
        packet, addr = sock.recvfrom(constants.PACKET_SIZE)
        packet_num = struct.unpack('>I', packet[:4])[0]
        checksum = struct.unpack('>I', packet[4:8])[0]
        size = struct.unpack('>I', packet[8:12])[0]
        packet_data = packet[12:]

        if zlib.crc32(packet[8:]) != checksum:
            print(f"Packet {packet_num} checksum mismatch")
            continue

        if exp_packet_num == packet_num:
            msg += packet_data
            sock.sendto(struct.pack('>I', exp_packet_num), addr)
            exp_packet_num += 1
        else:
            sock.sendto(struct.pack('>I', exp_packet_num - 1), addr)

        if len(msg) >= size:
            break

    return msg.decode(constants.ENCODING), addr
