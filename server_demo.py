from library.server import Server

SERVER_IP_ADRESS = ''

if __name__ == '__main__':

    server = Server()

    while True:

        write_message = "Ales je mrdkaaaaaaaaaaaa"
        server.message_send(message=write_message)
        message = server.message_read()
        print(message)

