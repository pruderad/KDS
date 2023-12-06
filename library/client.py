import socket
import json
import sys
import crcmod
import heapq
import hashlib
import numpy as np


class Client:
    def __init__(self, server_ip_adress: str, window_size: int, bufferSize: int = 1024) -> None:
        with open('./net_derper/Config.json', 'rb') as c_file:
            self.nd_config = json.load(c_file)
            self.ip_adress = self.nd_config['Data']['Connection']['TargetHostName']
            self.local_port = int(self.nd_config['Data']['Connection']['TargetPort'])
            self.target_port = int(self.nd_config['Acknowledgement']['Connection']['SourcePort'])

        self.server_ip_adress = server_ip_adress
        self.bufferSize = bufferSize
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.create_server()

        self.received_packet_ids = set()
        self.received_packets = []
        self.window_size = window_size
        self.window_start_id = None
        self.acked_packets = None

    def create_server(self) -> None:
        self.socket.bind((self.ip_adress, self.local_port))
        print(f'server with IP adress {self.ip_adress} is active')
        print("UDP server up and listening")

    def read_init_packet(self, packet: bytes) -> tuple:

        try:
            data = packet.decode()
            file_data = data.split(',')
        except Exception as e:
            return None, None, None

        file_name = file_data[0]
        file_length = file_data[1]
        file_hash = file_data[2]

        return file_name, file_length, file_hash


    def read_packet(self, block: bool = False) -> tuple:
        self.socket.setblocking(block)
        #TODO received packet might be limited by client address
        bytesAddressPair = self.socket.recvfrom(self.bufferSize)
        packet = bytesAddressPair[0]
        client_address = bytesAddressPair[1]

        # split the message and crc
        try:
            decoded_packet = packet.decode()
            print(decoded_packet)
            print()
            print()
            received_id = int(decoded_packet.split(',')[0])
            received_crc = int(decoded_packet[-10:])
            print('crc', received_crc)
            received_message = decoded_packet[:-10]

        except Exception as e:
            print(e)
            return False, None, None, None
        
        valid = self.getCRC_validity(received_message, received_crc)

        # remove id from message
        splits = list(received_message.split(','))
        message = ''
        for split in splits[1:]:
            message += split

        return valid, received_message, received_id, client_address

    def getCRC_validity(self, received_message, received_crc):
        crc32_func = crcmod.predefined.mkCrcFun('crc-32')
        computed_crc = crc32_func(received_message.encode())
        valid = computed_crc == received_crc

        return valid

    def send_bytes(self, bytesToSend :bytes) -> None:
        self.socket.sendto(bytesToSend, (self.ip_adress, self.target_port))

    def is_received(self, id: int) -> None:
        return id in self.received_packet_ids

    def send_ack(self, id: int, ack: bool) -> None:
        # TODO() send ack/nack

        ack_byte = '1'.encode()
        if not ack:
            ack_byte = '-1'.encode()

        id_str = str(id)
        id_byte = id_str.encode()

        message = id_byte + ','.encode() + ack_byte

        self.send_bytes(message)


    def id_in_window(self, packet_id: int) -> bool:
        return packet_id >= self.window_start_id and packet_id < self.window_start_id + self.window_size

    def receive_file(self):

        self.window_start_id = 0
        self.acked_packets = [False for _ in range(self.window_size)]

        while True:

            # receive message
            print('waiting for message')
            valid, received_message, received_id, _ = self.read_packet(block=True)
            print('continuing')
            if valid and self.id_in_window(received_id):
                # acknowledge valid message
                self.send_ack(received_id, True)
                print('sent ack')
                self.acked_packets[received_id] = True

                # check end of sequence
                if received_message == 'STOP':
                    print('Received STOP')
                    break

                # register message if not received
                if received_id not in self.received_packet_ids:
                    heapq.heappush(self.received_packets, [received_id, received_message])
                    print(len(self.received_packets))
                    # shift the sliding window
                    while self.acked_packets[self.window_start_id]:
                        self.acked_packets.append(False)
                        self.window_start_id += 1

            # ack all past packets
            elif received_id is not None and received_id < self.window_start_id:
                print('sending ack')
                self.send_ack(received_id, True)

            # nack invalid packets in current window
            elif received_id is not None and self.id_in_window(received_id):
                self.send_ack(received_id, False)

            else:
                print('Message from future You Stupid')

        valid = self.save_file_from_packets(self.received_packets)
        print(f'Received: {valid}')


    def save_file_from_packets(self, packets_queue):
        _, init_packet = heapq.heappop(packets_queue)
        file_name, file_length, received_hash = self.read_init_packet(init_packet)

        with open(file_name, 'wb') as file:
            while len(packets_queue) > 0:
                packet_id, packet = heapq.heappop(packets_queue)
                file.write(packet)

                # check the file validity
            calculated_hash = hashlib.file_digest(file, 'sha256').hexdigest()

        return calculated_hash == received_hash






