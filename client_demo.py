from library.client import Client

server_ip = '127.0.0.1' 
server_port = 20001
client = Client(server_ip=server_ip, server_port=server_port, bufferSize=1024)

init_message = 'Init message from client'
client.message_send(message=init_message)

while True:
    message = client.message_read()

    print(f'message from server: {message}')