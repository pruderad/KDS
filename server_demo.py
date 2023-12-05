from library.server import Server

server = Server(ip_adress='127.0.0.1', local_port=20001, bufferSize=1024)
server.create_server()

read_message, client_ip = server.message_read()
print(f'client message: {read_message}, client IP: {client_ip}')

while True:

    write_message = "Ales je mrdka"
    server.message_send(message=write_message, client_adress=client_ip)

