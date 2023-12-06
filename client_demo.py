from library.client import Client
import time

SERVER_IP_ADRESS = '147.32.215.117'

if __name__ == '__main__':

    client = Client(server_ip_adress=SERVER_IP_ADRESS, window_size=10)
    client.receive_file()
    print('done')