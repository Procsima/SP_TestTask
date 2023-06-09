import sys
import socket
import safe_udp


def main():
    IP = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8888
    NAME = sys.argv[3] if len(sys.argv) > 3 else 'Client'

    print(f'ip: {IP}, port: {PORT}, name: {NAME}\nprint # to disconnect')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    safe_udp.send(NAME, sock, (IP, PORT))
    res, addr = safe_udp.receive(sock)
    if res == '0':
        print('ERROR: This name is taken!')
        sys.exit(0)
    else:
        print('LOG: Connected')
    while True:
        cmd = input()
        safe_udp.send(NAME + ' ' + cmd, sock, (IP, PORT))
        queue_name = cmd.split()[0]
        if queue_name == '#':
            print('LOG: Turning off')
            sys.exit(0)
        msg = cmd[len(queue_name) + 1:]
        if not msg:
            data, addr = safe_udp.receive(sock)
            print(data)


if __name__ == '__main__':
    main()
