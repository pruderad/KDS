import socket
import json
import sys
import crcmod
import threading
import os
import hashlib
import heapq
import time

import numpy as np


class Server:
    def __init__(self, ack_timout_s: float, ip_adress: str = "127.0.0.1", bufferSize: int = 1024, sender_freq_hz: float = 100, reciever_freq_hz: float = 100) -> None:
        
        with open('./net_derper/Config.json', 'rb') as c_file:
            self.nd_config = json.load(c_file)
            self.local_port = int(self.nd_config['Acknowledgement']['Connection']['TargetPort'])
            self.target_port = int(self.nd_config['Data']['Connection']['SourcePort'])
            #self.client_ip_adress = self.nd_config['Data']['Connection']['TargetHostName']
            self.client_ip_adress = "127.0.0.1"

        self.ip_adress = ip_adress
        self.bufferSize = bufferSize
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.create_server()

        self.crc_size = 4 # in bytes

        # shared resources between sender and reciever
        self.remaining_window_packets = []  # priority queue of packets to be sent in future iteration of sender thread [id, packet]
        self.packets_to_resend = []  # priority queue of packets that need to be resent in future iteration of sender thread [id, packet]
        self.acknowledged_packets = None  # np.array containing TRUE / FALSE for each packet indicating whether the packet was recieved --> shift the window here
        self.packets_sent_time = None  # np.array of times when the packets were sent
        self.com_finished = False  # indicates whether the sending process is done --> end the threads
        self.lock = threading.Lock()  # mutex
        self.all_packets = None

        # time synchronization
        self.sender_freq_hz = sender_freq_hz
        self.reciever_freq_hz = reciever_freq_hz
        self.com_start_time = -1  # start of the communication
        self.ack_timeout_s = ack_timout_s

    def create_server(self) -> None:
        self.socket.bind((self.ip_adress, self.local_port))
        print(f'server with IP adress {self.ip_adress} is active')
        print("UDP server up and listening")

    def getCRC_validity(self, received_message, received_crc):
        crc32_func = crcmod.predefined.mkCrcFun('crc-32')
        computed_crc = crc32_func(received_message.encode())
        valid = computed_crc == received_crc

        return valid

    def message_read(self, block: bool = False) -> list:
        # TODO() check validity
        # TODO() add non blocking
        self.socket.setblocking(block)
        # TODO received packet might be limited by client address
        bytesAddressPair = self.socket.recvfrom(self.bufferSize)
        packet = bytesAddressPair[0]
        client_address = bytesAddressPair[1]

        # split the message and crc
        try:
            decoded_packet = packet.decode()
            received_id = int(decoded_packet.split(',')[0])
            received_crc = int(decoded_packet[-10:])
            received_message = decoded_packet[:-10]

        except Exception as e:
            return False, None, None, None

        valid = self.getCRC_validity(received_message, received_crc)

        # remove id from message
        splits = list(received_message.split(','))
        message = ''
        for split in splits[1:]:
            message += split

        return valid, received_message, received_id, client_address


    def send_bytes(self, bytesToSend :bytes) -> None:
        self.socket.sendto(bytesToSend, (self.client_ip_adress, self.target_port))

    def get_CRC(self, data):
        crc32_func = crcmod.predefined.mkCrcFun('crc-32')
        crc = crc32_func(data)
        crc_str = str(crc)
        crc_correct_len = crc_str.zfill(10)

        return crc_correct_len

    def open_file(self, path) -> tuple:
        # TODO() get filename, file length, file hash -> first packet

        with open(path, 'rb') as file:
            data = file.read()

            filename = os.path.basename(file.name)
            file_length = len(data)

            file_hash = hashlib.file_digest(file, 'sha256').hexdigest()

        return data, filename, file_length, file_hash

    def split_to_packets(self, path: str) -> list:
        # TODO() while not whole file in packets -> get idx -> get idx_size + crc_size -> fill remaining space with data
        data, filename, file_length, file_hash = self.open_file(path)
        packets = []

        init_packet = f"{filename},{file_length},{file_hash}".encode()
        packets.append(init_packet)

        id = 0
        while id < file_length:
            id_str = str(id)
            id_bytes = id_str.encode()
            id_size = len(id_bytes)

            data_len = self.bufferSize - id_size - self.crc_size - len(','.encode())  # TODO() possibly 10

            packet_data = data[id:id + data_len]
            packet_id_data = id_bytes + ','.encode() + packet_data

            crc = self.get_CRC(packet_id_data)
            crc_bytes = crc.encode()

            packet = packet_id_data + crc_bytes
            packets.append(packet)

            id += data_len
        return packets


    def parse_ack_message(self, message: str) -> tuple:
        ack = bool(message)
        return ack

    def serve_file(self, file_path: str, window_size: int) -> None:
        # TODO() create sender and listener threads and end them at the end of communication
        # TODO() load the file and split it to packets

        packets = self.split_to_packets(file_path)
        N = len(packets)

        # initialize the shared memmory structures
        self.remaining_window_packets = []
        self.packets_to_resend = []
        self.acknowledged_packets = np.zeros((N,), dtype=bool)
        self.packets_sent_time = - np.ones((N,), dtype=float)
        self.all_packets = packets
        self.window_size = window_size
        self.packet_ids_to_resend = set()  # do not add twice -- nack and timeout
        self.com_start_time = time.time()

        # initialize the threads
        data_thread = threading.Thread(target=self.data_sender_thread())
        ack_thread = threading.Thread(target=self.ack_reciever_thread())
        print('Initialize threads')

        # start the threads
        data_thread.start()
        ack_thread.start()

        # end the threads when done
        ack_thread.join()
        data_thread.join()


    def data_sender_thread(self):

        while True:

            # check if communication has ended
            with self.lock:
                if self.com_finished:
                    print('Ending data sender')
                    break

            # check and send one remaining file in the window
            with self.lock:
                new_packet = None
                if not len(self.remaining_window_packets) == 0:
                    # send remaining packet in current window
                    new_packet_id, new_packet = heapq.heappop(self.remaining_window_packets)

            if new_packet is not None:
                # update sent time
                with self.lock:
                    self.packets_sent_time[new_packet_id] = time.time() - self.com_start_time
                # send the packet
                self.send_bytes(new_packet)

            # check and send one remaining file to resend
            with self.lock:
                new_packet = None
                if not len(self.packets_to_resend) == 0:
                    new_packet_id, new_packet = heapq.heappop(self.packets_to_resend)

            if new_packet is not None:
                # update sent time
                with self.lock:
                    self.packets_sent_time[new_packet_id] = time.time() - self.com_start_time
                    if new_packet_id in self.packet_ids_to_resend:
                        self.packet_ids_to_resend.remove(new_packet_id)
                # send the packet
                self.send_bytes(new_packet)

            time.sleep(1 / self.sender_freq_hz)


    def ack_reciever_thread(self):

        window_start_idx = 0

        while True:
            # process incoming acknowledgement -- nonblocking
            valid, message, packet_id, _ = self.message_read(block=False)
            if valid:
                ack = self.parse_ack_message(message)
                if ack:
                    # acknowledge packet
                    self.acknowledged_packets[packet_id] = True

                    # shift the buffer
                    old_window_start_idx = window_start_idx
                    while self.acknowledged_packets[window_start_idx]:
                        window_start_idx += 1
                        if window_start_idx == len(self.all_packets) - 1:
                            # reached the end
                            print('All packets ackowledged --> ending ack reciever thread')
                            with self.lock:
                                self.com_finished = True
                                return

                    # get the new packets to send -- because if the window shift
                    if old_window_start_idx != window_start_idx:
                        new_packet_items = []
                        start_packet_id = min(old_window_start_idx + self.window_size, len(self.all_packets) - 1)
                        end_packet_id = max(window_start_idx + self.window_size, len(self.all_packets) - 1)
                        for new_packet_id in range(start_packet_id, end_packet_id):
                            new_packet_items.append(self.all_packets[new_packet_id, self.all_packets[new_packet_id]])

                        with self.lock:
                            for item in new_packet_items:
                                heapq.heappush(self.remaining_window_packets, item)

                else:
                    # resend packet
                    packet_to_resend = self.all_packets[packet_id]
                    with self.lock:
                        if packet_id not in self.packet_ids_to_resend:
                            heapq.heappush(self.packets_to_resend, [packet_id, packet_to_resend])
                            self.packet_ids_to_resend.add(packet_id)

            # check timeouts
            with self.lock:
                for packet_id in range(window_start_idx, min(window_start_idx + self.window_size, len(self.all_packets))):
                    if not self.acknowledged_packets[packet_id] and packet_id not in self.packet_ids_to_resend and self.packets_sent_time[packet_id] != -1:
                        cur_wait_time = time.time() - self.com_start_time - self.packets_sent_time[packet_id]
                        if cur_wait_time > self.ack_timeout_s:
                            packet_to_resend = self.all_packets[packet_id]
                            self.packet_ids_to_resend.add(packet_id)
                            heapq.heappush(self.packets_to_resend, [packet_id, packet_to_resend])

            time.sleep(1 / self.reciever_freq_hz)




