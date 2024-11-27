import socket
import threading
import time
import json

# Port number the application is working on (listening & sending)
APP_PORT = 12345

# Header used for message verification
VERYFICATION_HEADER = b'YELLMESSAGE'

# Global variable for storing messages waiting to be displayed
message_queue = []

# Global variable for storing user alias
alias = None

def init_alias():
    """
    Initialize the global user alias variable by asking the user for it. The
    alias is stored in a global variable and can be accessed from any function.
    The alias is stripped of leading and trailing whitespace.
    """
    global alias
    alias = input("Enter your alias: ").strip()

def format_message(message, adress):
    """
    Return a formatted string for displaying a message in the chat window.
    The message string includes the sender's alias and the sender's address.

    :param message: A dictionary containing the message's 'alias' and 'text'.
    :param adress:  The sender's address as a string.
    :return: A string representation of the message.
    """
    return f"{message['alias']} ({adress[0] + ':' + str(adress[1])}) : {message['text']}"

def start_listener():
    """
    Starts a thread that listens for incoming UDP messages on the specified
    APP_PORT and appends them to the global message_queue. The socket is bound
    to all available network interfaces. Each received message is decoded and
    stored with the sender's address for later display.
    """
    def listen():
        """
        Listens for incoming UDP messages on the specified APP_PORT and appends
        them to the global message_queue. The socket is bound to all available 
        network interfaces. Each received message is decoded and stored with the 
        sender's address for later display.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind(("", APP_PORT))  # Listening on all interfaces

            while True:
                data, address = server_socket.recvfrom(1024)
                if data.startswith(VERYFICATION_HEADER):  # Verify that message is sent by this application
                    global message_queue
                    message_queue.append(format_message(json.loads(data[len(VERYFICATION_HEADER):].decode()), address))  # Add message to queue to be displayed on update

    listener_thread = threading.Thread(target=listen, daemon=True)
    listener_thread.start()

def send(message):
    """
    Send the given message over the network using UDP broadcast to all devices
    on the same network that are listening on the APP_PORT.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(VERYFICATION_HEADER + json.dumps(message).encode('utf-8'), ("255.255.255.255", APP_PORT))  # Broadcast message on APP_PORT

def start_yeller():
    """
    Start a thread that constantly asks for user input. The input is sent
    over the network using the send() function. If the input is empty, only
    the message queue is updated. The message queue is cleared after each
    update.
    """
    while True:
        text = input("Send message: ").strip()
        print("\033[F\033[K", end="", flush=True)  # Delete old input query by moving cursor up and clearing line

        message = {
            "alias": alias,
            "text": text
            }

        # Only send messages with content, therefore allowing display updating using empty messages
        if message["text"] != "":
            send(message)

        # Update dispayed messages
        [print(msg) for msg in message_queue]
        message_queue.clear()

if __name__ == "__main__":
    init_alias()

    start_listener()

    # Wait for the listener to start
    time.sleep(0.1)

    start_yeller()
