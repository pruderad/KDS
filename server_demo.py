from library.server import Server
import time
import crcmod

SERVER_IP_ADRESS = ''

if __name__ == '__main__':

    server = Server()

    while True:

        write_message = "Ales je mrdka"



        server.message_send(message=write_message)
        #message = server.message_read()
        #print(message)
        time.sleep(0.5)

