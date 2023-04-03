import sys
import socket
import safe_udp
import msg_queue


def main():
    IP = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5555

    print(f'ip: {IP}, port: {PORT}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))

    queues = dict()
    clients = dict()

    while True:
        data, addr = safe_udp.receive(sock)
        if not data:
            for n, a in clients:
                if a[0] == addr:
                    clients.pop(n)
                    break
            continue
        client_name = data.split()[0]
        if len(data.split()) == 1:
            if client_name[0] == '!':
                if client_name[1:] in clients:
                    clients[client_name[1:]][1] = addr
                    continue
            if client_name in clients:
                safe_udp.send('0', sock, addr)
                print(f'LOG: Client with existing name {client_name} tried to connect')
            else:
                safe_udp.send('1', sock, addr)
                clients[client_name] = [addr, ['', 0]]
                print(f'LOG: Client "{client_name}" connected')
            continue

        queue_name = data.split()[1]
        if queue_name == '#':
            safe_udp.send('#', sock, clients[client_name][1])
            clients.pop(client_name)
            print(f'LOG: Client "{client_name}" disconnected')
            continue
        msg = data[len(queue_name) + len(client_name) + 2:]
        if queue_name in clients:
            safe_udp.send(client_name + ': ' + msg, sock, clients[queue_name][1])
        else:
            safe_udp.send("ERROR: No such client!", sock, clients[client_name][1])
            print('ERROR: No such client!')
        # if msg:
        #     if queue_name not in queues:
        #         queues[queue_name] = msg_queue.MsgQueue()
        #     queues[queue_name].put(msg)
        #     print(f'LOG: Got msg: {msg}')
        # else:
        #     if queue_name not in queues:
        #         print('ERROR: no such queue!')
        #         safe_udp.send("ERROR: No such queue!", sock, clients[client_name][1])
        #         # sock.sendto("ERROR: no such queue!".encode(constants.ENCODING), addr)
        #     else:
        #         if queues[queue_name].empty():
        #             queues.pop(queue_name)
        #             safe_udp.send(f'LOG: Queue {queue_name} deleted', sock, clients[client_name][1])
        #             # sock.sendto("Queue deleted".encode(constants.ENCODING), addr)
        #         else:
        #             safe_udp.send(queues[queue_name].get(), sock, clients[client_name][1])
        #             # sock.sendto(queues[name].get().encode(constants.ENCODING), addr)


if __name__ == '__main__':
    main()
