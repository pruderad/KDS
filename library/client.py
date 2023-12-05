import socket

 
class Client:
    def __init__(self, ip_adress: str, local_port: int = 20001, bufferSize: int = 1024) -> None:
        self.ip_adress = ip_adress
        self.local_port = local_port
        self.bufferSize = bufferSize
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def create_server(self) -> None:
        self.socket.bind((self.ip_adress, self.local_port))
        print(f'server with IP adress {self.ip_adress} is active')
        print("UDP server up and listening")

    def message_read(self) -> list:
        bytesAddressPair = self.socket.recvfrom(self.bufferSize)

        message = bytesAddressPair[0]
        client_address = bytesAddressPair[1]

        return message, client_address
    
    def message_send(self, message: str, client_adress: str) -> None:
        bytesToSend = str.encode(message)
        self.socket.sendto(bytesToSend, client_adress)




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