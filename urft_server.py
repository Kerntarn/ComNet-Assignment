import socket
import sys
import os
from datetime import datetime as dt

buf = 1024
timeout = 60

def start_server():

    if len(sys.argv) < 3:
        print("python urft_server.py <server_ip> <server_port>")
        sys.exit(1)

    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (sys.argv[1], int(sys.argv[2]))
    server_socket.bind(server_address)
    server_socket.settimeout(timeout)

    file_name = ''
    file_data = ""
    expected_seq = 0
    print("READY!")
    while 1:
        try:
            data, client_address = server_socket.recvfrom(buf + 40)
            packet_parts = data.decode('utf-8').split('|', 2)

            if len(packet_parts) < 2:
                continue

            seq = int(packet_parts[0])

            print(f"receiving SEQ: {seq} expect: {expected_seq}")
            if seq == -1:
                print("Done!")
                break
            if seq == -2:
                file_name = packet_parts[1]
                server_socket.sendto(f"ACK|{dt.now()}".encode('utf-8'), client_address)
                print("Got file name")
                continue

            if seq <= expected_seq:
                if seq == expected_seq:
                    file_data += packet_parts[1]
                    expected_seq += buf
                server_socket.sendto(f"ACK|{expected_seq}".encode('utf-8'), client_address)
                print(f"sending ACK: {expected_seq}")
        except socket.timeout:
            print("Client is gone")
            break
    server_socket.close()

    with open(f'{file_name}', "wb") as file:
        file.write(file_data.encode("utf-8"))

if __name__ == "__main__":
    start_server()
