# A Simple TCP client, used as a warm-up exercise for socket programming assignment.
# Course IELEx2001, NTNU

import random
import time
from socket import *

# Hostname of the server and TCP port number to use
HOST = "datakomm.work"
PORT = 1301

# The socket object (connection to the server and data excahgne will happen using this variable)
client_socket = None


def connect_to_server(host, port):
    """
    Try to establish TCP connection to the server (the three-way handshake).
    :param host: The remote host to connect to. Can be domain (localhost, ntnu.no, etc), or IP address
    :param port: TCP port to use
    :return: True when connection established, false otherwise
    """

    # TODO - implement this method
    #Remember to catch all possible exceptions the socket can throw in case you have not worked with exceptions,
    #the syntax is as follows:
    loc_bool = None
    global client_socket
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
         client_socket.connect((HOST, PORT))
         return True
    except IOError as e:
         print("Error happened:", e)
         return False


def close_connection():
    """
    Close the TCP connection to the remote server.
    :return: True on success, false otherwise
    """
    # TODO - implement this method
    global client_socket
    client_socket.close()
    print("Connection Closed")
    return True


def send_request_to_server(request):
    """
    :param request: The request message to send. Do NOT include the newline in the message!
    :return: True when message successfully sent, false on error.
    """
    # TODO - implement this method
    global client_socket
    request = request + "\n"
    in_bytes = request.encode()
    client_socket.send(in_bytes)
    return True

def read_response_from_server():
    """
    Wait for one response from the remote server.
    :return: The response received from the server, None on error. The newline character is stripped away
     (not included in the returned value).
    """
    global client_socket
    response = client_socket.recv(100)
    response_string = response.decode()
    return response_string


def run_client_tests():
    """
    Runs different "test scenarios" from the TCP client side
    :return: String message that represents the result of the operation
    """
    print("Simple TCP client started")
    if not connect_to_server(HOST, PORT):
        return "ERROR: Failed to connect to the server"

    print("Connection to the server established")
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    request = str(a) + "+" + str(b)

    if not send_request_to_server(request):
        return "ERROR: Failed to send valid message to server!"

    print("Sent ", request, " to server")
    response = read_response_from_server()
    if response is None:
        return "ERROR: Failed to receive server's response!"

    print("Server responded with: ", response)
    seconds_to_sleep = 2
    print("Sleeping %i seconds to allow simulate long client-server connection..." % seconds_to_sleep)
    time.sleep(seconds_to_sleep)

    request = "bla+bla"
    if not send_request_to_server(request):
        return "ERROR: Failed to send invalid message to server!"

    print("Sent " + request + " to server")
    response = read_response_from_server()
    if response is None:
        return "ERROR: Failed to receive server's response!"

    print("Server responded with: ", response)
    if not (send_request_to_server("game over") and close_connection()):
        return "ERROR: Could not finish the conversation with the server"

    print("Game over, connection closed")
    # When the connection is closed, try to send one more message. It should fail.
    if send_request_to_server("2+2"):
        return "ERROR: sending a message after closing the connection did not fail!"

    print("Sending another message after closing the connection failed as expected")
    return "Simple TCP client finished"


# Main entrypoint of the script
if __name__ == '__main__':
    result = run_client_tests()
    print(result)