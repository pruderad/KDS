import socket

 
class Server:
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

localIP     = "192.168.1.117"

localPort   = 20001

bufferSize  = 1024

 

msgFromServer       = "Hello UDP Client"

bytesToSend         = str.encode(msgFromServer)

 

# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 

# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

 

print("UDP server up and listening")

 

# Listen for incoming datagrams

while(True):

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    clientIP  = "Client IP Address:{}".format(address)
    
    print(clientMsg)
    print(clientIP)

   

    # Sending a reply to client

    UDPServerSocket.sendto(bytesToSend, address)

'''