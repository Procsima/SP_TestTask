import sys
import socket
import safe_udp
import threading


def client_input(NAME: str, IP: str, PORT: int, sock: socket.socket):
    while True:
        cmd = input()
        safe_udp.send(NAME + ' ' + cmd, sock, (IP, PORT))
        queue_name = cmd.split()[0]
        if queue_name == '#':
            print('LOG: Turning off')

            sys.exit(0)


def client_receive(NAME: str, IP: str, PORT: int, sock: socket.socket):
    safe_udp.send(f'!{NAME}', sock, (IP, PORT))
    while True:
        data, addr = safe_udp.receive(sock)
        if data == '#':
            sys.exit(0)
        print(data)


def main():
    IP = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5555
    NAME = sys.argv[3] if len(sys.argv) > 3 else 'Client'

    print(f'ip: {IP}, port: {PORT}, name: {NAME}\nprint # to disconnect')

    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    safe_udp.send(NAME, send_sock, (IP, PORT))
    res, addr = safe_udp.receive(send_sock)
    if res == '0':
        print('ERROR: This name is taken!')
        sys.exit(0)
    else:
        print('LOG: Connected')

    input_thread = threading.Thread(target=client_input, args=(NAME, IP, PORT, send_sock))
    input_thread.start()
    client_receive(NAME, IP, PORT, receive_sock)


if __name__ == '__main__':
    main()
