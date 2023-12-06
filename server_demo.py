from library.server import Server
import time
import crcmod

SERVER_IP_ADRESS = ''
FILE_PATH = './data/n1_driver.jpg'

if __name__ == '__main__':

    server = Server(ack_timout_s=0.1, sender_freq_hz=100, reciever_freq_hz=100)
    server.serve_file(file_path=FILE_PATH, window_size=10)

    print('done')
