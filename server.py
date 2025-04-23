import socket
import ssl
import threading

# Itinerary shared by all clients
itinerary = []
clients = []

def handle_client(control_conn, data_conn, addr):
    print(f"[+] Client connected from {addr}")
    try:
        while True:
            cmd = control_conn.recv(1024).decode()
            if not cmd:
                break

            print(f"[DEBUG] Received command: {cmd}")

            if cmd.startswith("ADD"):
                place = cmd.split(" ", 1)[1]
                itinerary.append(place)
                print(f"[+] Added: {place}")
                for client in clients:
                    try:
                        client[1].sendall(f"UPDATE {place}\n".encode())
                    except:
                        continue

            elif cmd.strip() == "VIEW":
                response = "\n".join(itinerary) + "\n"
                data_conn.sendall(response.encode())

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        print(f"[-] Client {addr} disconnected")
        clients.remove((control_conn, data_conn))
        control_conn.close()
        data_conn.close()

def main():
    # SSL setup
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert/server.crt", keyfile="cert/server.key")

    # Raw sockets (no libraries)
    control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_sock.bind(("localhost", 5000))
    data_sock.bind(("localhost", 5001))

    control_sock.listen()
    data_sock.listen()
    print("[SERVER] Listening on ports 5000 (control) and 5001 (data)...")

    while True:
        # Accept data first, then control to avoid race condition
        data_conn, _ = data_sock.accept()
        control_conn, addr = control_sock.accept()

        # SSL wrap
        control_conn = context.wrap_socket(control_conn, server_side=True)
        data_conn = context.wrap_socket(data_conn, server_side=True)

        clients.append((control_conn, data_conn))
        thread = threading.Thread(target=handle_client, args=(control_conn, data_conn, addr))
        thread.start()

if __name__ == "__main__":
    main()
