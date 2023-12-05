from library.server import Server
import time

server = Server(ip_adress='147.32.215.93', local_port=15000, bufferSize=1024)
server.create_server()
#server.socket.listen(1)


while True:
    message = server.message_read()
    print(message)
    server.message_send('je to pravda', ('147.32.215.97', 14001))
