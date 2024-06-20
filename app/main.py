import socket


def main():

    
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    client_socket, client_address = server_socket.accept() # wait for client

    print("server started")
    client_socket.send(b"+PONG\r\n")

    client_socket.close() # close connection


if __name__ == "__main__":
    main()
