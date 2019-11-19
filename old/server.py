import socket
import time
import threading
import select
from threading import Thread
from socket import AF_INET, SOCK_STREAM


HOST = '127.0.0.1'
PORT = 6663
BUFF = 4096
UTF8 = 'utf-8'

server_socket = socket.socket(AF_INET, SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.listen(5)

list_of_sockets = [server_socket]
adresses = {}


def receive(client, address):

    main_flag = True

    while main_flag:
        try:
            data = client.recv(BUFF)
            time.sleep(0.4)
            if len(data):
                print(data.decode(UTF8))
            
                Thread(target=broadcast,
                        args=(data, client),
                        daemon=True).start()

            print(threading.active_count())

        except KeyboardInterrupt as e:
            print('SERVER CLOSED', str(e))
            Thread(target=broadcast,
                   args=(b'Server closed',),
                   daemon=True)
            for each in list_of_sockets:
                each.close()
            main_flag = False
        except ConnectionResetError:
            Thread(target=broadcast,
                   args=(f'{address} disconnected'.encode(UTF8),),
                   daemon=True).start()
            client.close()
            list_of_sockets.remove(client)
            main_flag = False


def send(client, data):
    try:
        client.send(data)
    except KeyboardInterrupt as e:
        print(e)


def broadcast(data, client=None):
    for socket in list_of_sockets:
        try:
            if socket != server_socket:
                if socket != client:
                    socket.send(data)
        except BrokenPipeError:
            msg = f'{adresses[socket]} disconnected'
            Thread(target=broadcast,
                   args=(msg.encode(UTF8)),
                   daemon=True).start()
            list_of_sockets.remove(client)
        except:
            pass


if __name__ == "__main__":
    while True:
        try:
            client_object, client_address = server_socket.accept()
            list_of_sockets.append(client_object)
            adresses[client_object] = client_address
            msg = f'{client_address} connected'
            print(msg)

            Thread(target=broadcast,
                    args=(msg.encode(UTF8),),
                    daemon=True).start()

            Thread(target=receive,
                    args=(client_object,
                    client_address),
                    daemon=True).start()

        except ConnectionAbortedError:
            pass
        except TypeError as e:
            print('error is here', str(e))
            