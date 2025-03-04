import socket
import sys
from datetime import datetime as dt

buf = 1024
timeout = 0.25
sep = '/||/'

def start_client():

    if len(sys.argv) < 4:
        print("python urft_client.py <file_path> <server_ip> <server_port>")
        sys.exit(1)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)
    server_address = (sys.argv[2], int(sys.argv[3]))
    client_socket.setblocking(True)

    current_ack = 0

    with open(sys.argv[1], 'rb') as file:
        file_data = file.read()
        print("Read file")

    file_size = len(file_data)

    while 1:
        sender_time = dt.now()
        packet = f'-2{sep}{sys.argv[1]}'.encode('utf-8')
        client_socket.sendto(packet, server_address)
        try:
            ack_data, server = client_socket.recvfrom(buf) 
            ack, time = ack_data.decode('utf-8').split(sep)        #expect 2
            if ack != "ACK": continue

            time = dt.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
            rtt = (time.microsecond - sender_time.microsecond) * 0.000001
            client_socket.settimeout(timeout)
            print(f"start sending data with RTT: {rtt}")
            break

        except socket.timeout:
            print("--Timeout Retransmission--")

    while 1:
        if current_ack == -1: break

        if current_ack >= file_size:
            packet = f'-1{sep}FIN'.encode('utf-8')
            client_socket.sendto(packet, server_address)
            print(f"Sending FIN: {seq}")

        print(f"Sending SEQ: {current_ack} - {file_size - buf}")
        for seq in range(current_ack, file_size, buf):         #send many at the same time
            chunk = file_data[seq : seq + buf]
            packet = f"{seq}{sep}".encode('utf-8') + chunk
            client_socket.sendto(packet, server_address)

        try:
            while 1:
                ack_data, server = client_socket.recvfrom(40)           #Header size
                ack_parts = ack_data.decode('utf-8').split(sep)        #expect 2

                flag = ack_parts[0]
                current_ack = int(ack_parts[1])
                print(f'Furthest {flag}: {current_ack}')

                if flag == 'FIN':
                    break

        except socket.timeout:
            print("--Timeout Retransmission--")

    print("File sent successfully!")
    client_socket.close()

if __name__ == "__main__":
    
    start_client()


