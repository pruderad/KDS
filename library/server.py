import socket
import json
import sys
import crcmod

 
class Server:
    def __init__(self, ip_adress: str = "127.0.0.1", bufferSize: int = 1024) -> None:
        
        with open('./net_derper/Config.json', 'rb') as c_file:
            self.nd_config = json.load(c_file)
            self.local_port = int(self.nd_config['Acknowledgement']['Connection']['TargetPort'])
            self.target_port = int(self.nd_config['Data']['Connection']['SourcePort'])
            #self.client_ip_adress = self.nd_config['Data']['Connection']['TargetHostName']
            self.client_ip_adress = '127.0.0.1'

        self.ip_adress = ip_adress
        self.bufferSize = bufferSize
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
        self.create_server()

    def create_server(self) -> None:
        self.socket.bind((self.ip_adress, self.local_port))
        print(f'server with IP adress {self.ip_adress} is active')
        print("UDP server up and listening")

    def message_read(self) -> list:
        bytesAddressPair = self.socket.recvfrom(self.bufferSize)

        message = bytesAddressPair[0]
        client_address = bytesAddressPair[1]

        return message, client_address
    
    def message_send(self, message: str) -> None:
        # TODO() message creating logic
        #bytesToSend = str.encode(message)

        crc32_func = crcmod.predefined.mkCrcFun('crc-32')
        crc = crc32_func(message.encode())
        message_with_crc = f"{message},{crc}"
        print(crc)

        bytesToSend = str.encode(message_with_crc)

        # TODO() register for error handling
        self.send_bytes(bytesToSend)


    def send_bytes(self, bytes):

        self.socket.sendto(bytes, (self.client_ip_adress, self.target_port))

