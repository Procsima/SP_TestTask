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
    clients = set()

    while True:
        data, addr = safe_udp.receive(sock)
        # data, addr = sock.recvfrom(constants.BUFFER_SIZE)
        client_name = data.split()[0]
        if len(data.split()) == 1:
            if client_name in clients:
                safe_udp.send('0', sock, addr)
                print('Client with existing name tried to connect')
            else:
                safe_udp.send('1', sock, addr)
                clients.add(client_name)
                print(f'LOG: Client {client_name} connected')
            continue

        queue_name = data.split()[1]
        msg = data[len(queue_name) + len(client_name) + 2:]
        if msg:
            if queue_name not in queues:
                queues[queue_name] = queue.Queue(constants.QUEUE_MAX_SIZE)
            queues[queue_name].put(msg)
            print(f'LOG: Got msg: {msg}')
        else:
            if queue_name not in queues:
                print('ERROR: no such queue!')
                safe_udp.send("ERROR: no such queue!", sock, addr)
                # sock.sendto("ERROR: no such queue!".encode(constants.ENCODING), addr)
            else:
                if queues[queue_name].empty():
                    queues.pop(queue_name)
                    safe_udp.send("Queue deleted", sock, addr)
                    # sock.sendto("Queue deleted".encode(constants.ENCODING), addr)
                else:
                    safe_udp.send(queues[queue_name].get(), sock, addr)
                    # sock.sendto(queues[name].get().encode(constants.ENCODING), addr)


if __name__ == '__main__':
    main()
