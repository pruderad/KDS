# Server

import socket
import crcmod
import pickle

def calculate_crc(data):
    crc32 = crcmod.predefined.Crc('crc-32')
    crc32.update(data)
    return crc32.crcValue

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8888))
    server_socket.listen(1)
    print("Server listening on port 8888...")

    connection, client_address = server_socket.accept()
    print("Connection from", client_address)

    try:
        while True:
            data = connection.recv(1024)
            if not data:
                break

            received_data, received_crc = pickle.loads(data)
            calculated_crc = calculate_crc(received_data)

            if calculated_crc == received_crc:
                print("Received data:", received_data.decode())
                response = "ACK"
            else:
                print("CRC check failed. Discarding data.")
                response = "NACK"

            connection.sendall(response.encode())

    finally:
        connection.close()

if __name__ == "__main__":
    server()
