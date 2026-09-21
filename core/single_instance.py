import socket
import sys
import threading

PORT = 54312

def handle_client(conn, app):
    try:
        data = conn.recv(1024)
        if data == b"SHOW":
            # Schedule the UI action on the main thread
            app.after(0, app._show_window)
    except Exception:
        pass
    finally:
        conn.close()

def listen_for_instances(server, app):
    while True:
        try:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, app), daemon=True).start()
        except Exception:
            break

def check_and_bind():
    """
    Attempts to bind to the local port.
    If it fails, assumes another instance is running, sends SHOW, and exits immediately.
    Returns the server socket if successful.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(("127.0.0.1", PORT))
        server.listen(5)
        return server
    except OSError:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", PORT))
            client.sendall(b"SHOW")
            client.close()
        except Exception:
            pass
        sys.exit(0)

def start_listener(server, app):
    """Starts listening on the bound server socket."""
    threading.Thread(target=listen_for_instances, args=(server, app), daemon=True).start()
    app._single_instance_server = server
