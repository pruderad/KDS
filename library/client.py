import socket
import json
import sys
import crcmod

class Client:
    def __init__(self, server_ip_adress: str, bufferSize: int = 1024) -> None:
        with open('./net_derper/Config.json', 'rb') as c_file:
            self.nd_config = json.load(c_file)
            self.ip_adress = self.nd_config['Data']['Connection']['TargetHostName']
            self.local_port = int(self.nd_config['Data']['Connection']['TargetPort'])
            self.target_port = int(self.nd_config['Acknowledgement']['Connection']['SourcePort'])

        self.server_ip_adress = server_ip_adress
        self.bufferSize = bufferSize
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.create_server()

    def create_server(self) -> None:
        self.socket.bind((self.ip_adress, self.local_port))
        print(f'server with IP adress {self.ip_adress} is active')
        print("UDP server up and listening")

    def message_read(self) -> list:
        bytesAddressPair = self.socket.recvfrom(self.bufferSize)
        packet = bytesAddressPair[0]
        client_address = bytesAddressPair[1]

        # split the message and crc
        try:
            decoded_packet = packet.decode()
            recieved_crc = int(decoded_packet[-10:])
            received_message = decoded_packet[:-10]

        except Exception as e:
            return False, ' ', ' '
        
        # chec validity of the recieved data with crc
        crc32_func = crcmod.predefined.mkCrcFun('crc-32')
        computed_crc = crc32_func(received_message.encode())
        print(computed_crc, recieved_crc)   
        valid = computed_crc == recieved_crc

        return valid, received_message, client_address
    
    def message_send(self, message: str) -> None:
        # TODO() message creating logic
        bytesToSend = str.encode(message)

        # TODO() register for error handling
        self.send_bytes(bytesToSend)

    def send_bytes(self, bytes):
        self.socket.sendto(bytes, (self.server_ip_adress, self.target_port))

