import queue
import sys
import socket
import constants
import safe_udp


def main():
    IP = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8888

    print(f'ip: {IP}, port: {PORT}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))

    queues = dict()

    while True:
        data, addr = safe_udp.receive(sock)
        # data, addr = sock.recvfrom(constants.BUFFER_SIZE)
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
                safe_udp.send("ERROR: no such queue!", sock, addr)
                # sock.sendto("ERROR: no such queue!".encode(constants.ENCODING), addr)
            else:
                if queues[name].empty():
                    queues.pop(name)
                    safe_udp.send("Queue deleted", sock, addr)
                    # sock.sendto("Queue deleted".encode(constants.ENCODING), addr)
                else:
                    safe_udp.send(queues[name].get(), sock, addr)
                    # sock.sendto(queues[name].get().encode(constants.ENCODING), addr)


if __name__ == '__main__':
    main()
