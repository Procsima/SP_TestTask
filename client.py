import queue
import sys
import socket
import constants
import asyncio


def main():
    IP = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8888
    NAME = sys.argv[3] if len(sys.argv) > 3 else 'Client'

    print(f'ip: {IP}, port: {PORT}, name: {NAME}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        cmd = input()
        sock.sendto(cmd.encode(constants.ENCODING), (IP, PORT))
        name = cmd.split()[0]
        msg = cmd[len(name) + 1:]
        if not msg:
            data, addr = sock.recvfrom(constants.BUFFER_SIZE)
            print(data.decode(constants.ENCODING))


if __name__ == '__main__':
    main()