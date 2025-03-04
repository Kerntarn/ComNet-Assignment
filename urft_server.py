import socket
import sys
import os
from datetime import datetime as dt

buf = 1024
timeout = 60
sep = '/||/'

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
    wndw = {}

    print("READY!")
    while 1:
        try:
            data, client_address = server_socket.recvfrom(buf + 20)
            packet_parts = data.decode('utf-8').split(sep)

            seq = int(packet_parts[0])
            payload = packet_parts[1]
            print(f"receiving SEQ: {seq} expect: {expected_seq}")

            if seq == -1:           #end
                print("Done!")
                packet = f'FIN{sep}{seq}'.encode('utf-8')
                server_socket.sendto(packet, client_address)
                break

            if seq == -2:           #Init
                file_name = payload
                server_socket.sendto(f"ACK{sep}{dt.now()}".encode('utf-8'), client_address)
                print("Got file name")
                continue

            wndw[seq] = payload

            while expected_seq in wndw.keys():
                file_data += wndw[expected_seq]
                expected_seq += buf

            server_socket.sendto(f"ACK{sep}{expected_seq}".encode('utf-8'), client_address)
            print(f"sending ACK: {expected_seq}")

        except socket.timeout:
            print("Client is gone")
            break

        
    server_socket.close()

    with open(f'{file_name}', "wb") as file:
        file.write(file_data.encode("utf-8"))

if __name__ == "__main__":
    start_server()
