import socket
import ssl
import threading

def receive_updates(data_sock):
    while True:
        try:
            msg = data_sock.recv(1024).decode()
            if msg:
                print(f"[SERVER] {msg.strip()}")
        except:
            break

def main():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # Raw sockets
    control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect data first (must match server)
    data_sock.connect(('localhost', 5001))
    control_sock.connect(('localhost', 5000))

    # Wrap with SSL
    control_ssl = context.wrap_socket(control_sock, server_hostname='localhost')
    data_ssl = context.wrap_socket(data_sock, server_hostname='localhost')

    print("[CLIENT] Connected to server. Use ADD <place> or VIEW")

    threading.Thread(target=receive_updates, args=(data_ssl,), daemon=True).start()

    while True:
        msg = input("> ")
        if msg.strip().upper() == "VIEW":
            control_ssl.sendall(msg.encode())
            response = data_ssl.recv(4096).decode()
            print(f"[Itinerary]\n{response}")
        elif msg.startswith("ADD "):
            control_ssl.sendall(msg.encode())
        else:
            print("[!] Invalid command. Use ADD <place> or VIEW")

if __name__ == "__main__":
    main()
