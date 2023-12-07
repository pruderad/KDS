from library.server import Server
import time
import crcmod

SERVER_IP_ADRESS = ''
FILE_PATH = './data/fel02.jpeg'

if __name__ == '__main__':

    server = Server(ack_timout_s=0.05, sender_freq_hz=1000, reciever_freq_hz=1200)
    server.serve_file(file_path=FILE_PATH, window_size=1)

    print('done')
