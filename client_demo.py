from library.client import Client
import time

SERVER_IP_ADRESS = '147.32.215.69'

if __name__ == '__main__':

    client = Client(server_ip_adress=SERVER_IP_ADRESS)

    while True:
        message = client.message_read()
        print(message)
        client.message_send('je to pravda -- Ales je fakt mrdka')
