from library.server import Server
import time
import crcmod

SERVER_IP_ADRESS = ''
FILE_PATH = './data/ajm.txt'

if __name__ == '__main__':

    server = Server(ack_timout_s=0.1, sender_freq_hz=500, reciever_freq_hz=500)
    server.serve_file(file_path=FILE_PATH, window_size=50)

    print('done')
