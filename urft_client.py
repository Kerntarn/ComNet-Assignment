import socket
import sys
from datetime import datetime as dt

buf = 1024
timeout = 1

def start_client():

    if len(sys.argv) < 4:
        print("python urft_client.py <file_path> <server_ip> <server_port>")
        sys.exit(1)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)
    server_address = (sys.argv[2], int(sys.argv[3]))
    client_socket.setblocking(True)  


    seq = 0

    with open(sys.argv[1], 'rb') as file:
        file_data = file.read()
        print("Read file")

    while 1:
        sender_time = dt.now()
        packet = f'-2|{sys.argv[1]}'.encode('utf-8')
        client_socket.sendto(packet, server_address)
        try:
            ack_data, server = client_socket.recvfrom(buf) 
            if server != server_address: 
                print("Who the f are you?")
                continue
            ack_parts = ack_data.decode('utf-8').split('|')        #expect 2

            if len(ack_parts) == 2 and ack_parts[0] == 'ACK':
                time = ack_parts[1]
                time = dt.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                rtt = (time.microsecond - sender_time.microsecond) * 0.000001
                client_socket.settimeout(rtt * 1.5)
                print(f"start sending data with RTT: {rtt}")
                break

        except socket.timeout:
            print("--Timeout Retransmission--")

    for i in range(0, len(file_data), buf):
        chunk = file_data[i : i + buf]
        packet = f"{seq}|".encode('utf-8') + chunk
        
        while 1:
            client_socket.sendto(packet, server_address)
            print(f"Sending SEQ: {seq}")
            try:
                ack_data, server = client_socket.recvfrom(40)   #Header size
                if server != server_address: 
                    print("Who the f are you?")
                    continue
                ack_parts = ack_data.decode('utf-8').split('|')        #expect 2

                if len(ack_parts) == 2 and ack_parts[0] == 'ACK':
                    ack_num = int(ack_parts[1])
                    print(f'Receiving ACK: {ack_num} expect: {seq + buf}')
                    if ack_num == seq + buf:
                        seq += buf
                        break

            except socket.timeout:
                print("--Timeout Retransmission--")

    eof_packet = f'-1|FIN'.encode('utf-8')
    client_socket.sendto(eof_packet, server_address)

    print("File sent successfully!")
    client_socket.close()

if __name__ == "__main__":
    
    start_client()


