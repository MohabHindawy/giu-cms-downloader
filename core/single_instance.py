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

def setup_single_instance(app):
    """
    Attempts to bind to the local port.
    If it fails, assumes another instance is running, sends SHOW, and exits.
    If it succeeds, starts a background thread to listen for SHOW commands.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(("127.0.0.1", PORT))
        server.listen(5)
        # Start listening in the background
        threading.Thread(target=listen_for_instances, args=(server, app), daemon=True).start()
        # Keep a reference to the server so it doesn't get garbage collected
        app._single_instance_server = server
    except OSError:
        # Address already in use, send SHOW to existing instance
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", PORT))
            client.sendall(b"SHOW")
            client.close()
        except Exception:
            pass
        sys.exit(0)
