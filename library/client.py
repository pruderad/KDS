import socket

class Client:
    def __init__(self, server_ip: str, server_port: int, bufferSize: int = 1024) -> None:
        self.server_ip = server_ip
        self.server_port = server_port
        self.bufferSize = bufferSize
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def message_send(self, message: str) -> None:
        bytesToSend = str.encode(message)
        self.socket.sendto(bytesToSend, (self.server_ip, self.server_port))

    def message_read(self) -> str:
        return self.socket.recvfrom(self.bufferSize)




'''
msgFromClient       = "Hello UDP Server"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 20001)

bufferSize          = 1024

 

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 

# Send to server using created UDP socket


UDPClientSocket.sendto(bytesToSend, serverAddressPort)



msgFromServer = UDPClientSocket.recvfrom(bufferSize)


msg = "Message from Server - {}".format(msgFromServer[0])

print(msg)
'''