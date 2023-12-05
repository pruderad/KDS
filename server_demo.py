from library.server import Server

SERVER_IP_ADRESS = '147.32.215.97'

if __name__ == '__main__':

    server = Server(ip_adress=SERVER_IP_ADRESS)

    while True:

        write_message = "Ales je mrdkaaaaaaaaaaaa"
        server.message_send(message=write_message)
        message = server.message_read()
        print(message)

