import socket
import threading
import time

# Port number the application is working on (listening & sending)
APP_PORT = 12345

def start_listener():
    """
    Start a thread that listens on the given APP_PORT and prints all
    incoming messages to the console.
    """
    def listen():
        """
        Listen for incoming UDP messages on APP_PORT and print them to the console.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind(("", APP_PORT))  # Listening on all interfaces
            print(f"Server listening on 0.0.0.0:{APP_PORT}")

            while True:
                data, address = server_socket.recvfrom(1024)
                print(f"Received '{data.decode()}' from {address}")

    listener_thread = threading.Thread(target=listen, daemon=True)
    listener_thread.start()

def send(message):
    """
    Send a UDP message to all devices in the local network using the
    given APP_PORT. The message is broadcasted to all devices in the
    network, meaning that no specific recipient is needed. The message
    is first printed to the console, then sent over the network.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            print(f"Message sent: '{message}'")
            sock.sendto(message.encode(), ("255.255.255.255", APP_PORT))  # Broadcast message on APP_PORT
        except Exception as e:
            print(f"Error while sending: {e}")

def start_yeller():
    """
    Start an infinite loop that waits for user input. The user is
    asked to input a message, and that message is then sent over the
    network using the send() function. This function does not return
    until the program is terminated.
    """
    while True:
        message = input("Send message: ").strip()
        send(message)

if __name__ == "__main__":
    start_listener()

    # Wait for the listener to start
    time.sleep(0.1)

    start_yeller()
