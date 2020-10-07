#################################################################################
# A Chat Client application. Used in the course IELEx2001 Computer networks, NTNU
#################################################################################

from socket import *
import time


# --------------------
# Constants
# --------------------
# The states that the application can be in
states = [
    "disconnected",  # Connection to a chat server is not established
    "connected",  # Connected to a chat server, but not authorized (not logged in)
    "authorized"  # Connected and authorized (logged in)
]
TCP_PORT = 1300  # TCP port used for communication
SERVER_HOST = "datakomm.work"  # Set this to either hostname (domain) or IP address of the chat server

# --------------------
# State variables
# --------------------
current_state = "disconnected"  # The current state of the system
# When this variable will be set to false, the application will stop
must_run = True
# Use this variable to create socket connection to the chat server
# Note: the "type: socket" is a hint to PyCharm about the type of values we will assign to the variable
client_socket = None  # type: socket


def quit_application():
    """ Update the application state so that the main-loop will exit """
    # Make sure we reference the global variable here. Not the best code style,
    # but the easiest to work with without involving object-oriented code
    global must_run
    must_run = False


def send_command(command, arguments):
    """
    Send one command to the chat server.
    :param command: The command to send (login, sync, msg, ...(
    :param arguments: The arguments for the command as a string, or None if no arguments are needed
        (username, message text, etc)
    :return:
    """
    global client_socket
    if arguments == "":
        msg_to_send = (command).encode()
    else:
        msg_to_send = (command + arguments).encode()
    try:
        client_socket.send(msg_to_send)
        return True
    except IOError as e:
        print("Could not send: ",e)
        pass
    pass


def read_one_line():
    """
    Read one line of text from a socket
    :param sock: The socket to read from.
    :return:
    """
    newline_received = False
    message = ""
    while not newline_received:
        character = client_socket.recv(1).decode()
        if character == '\n':
            newline_received = True
        elif character == '\r':
            pass
        else:
            message += character
    return message


def get_servers_response():
    """
    Wait until a response command is received from the server
    :return: The response of the server, the whole line as a single string
    """
    global current_state
    response = read_one_line()
    if response == "modeok":
        current_state = "authorized"
    return response


def connect_to_server():
    # Must have these two lines, otherwise the function will not "see" the global variables that we will change here
    global client_socket
    global current_state

    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST,TCP_PORT))
        current_state = "connected"
        pass
    except IOError as e:
        print("Error Happened: ", e)
        print(current_state)
        return False

    send_command("sync", ""+"\n")

    print("Server responded with: ", get_servers_response())
    print(current_state)


def disconnect_from_server():
    global client_socket
    global current_state
    try:
        client_socket.close()
        current_state = "disconnected"
        print(current_state)
        return True
    except IOError as e:
        print("could not disconnect")
        pass
    pass


def client_login():
    """
    Sends a command with a username to server
    :return:
    """
    _username = input("Choose thy name: ")
    send_command("login", " "+_username+"\n")
    print(get_servers_response())
    pass

def public_msg():
    """
    :return:
    """
    msg = input("What do you desire to say? ")
    send_command("msg", " " + msg + "\n")
    print(get_servers_response())
    pass

def private_msg():
    _who = input("Who is this for? ")
    _what = input("What do you want to say? ")
    send_command("privmsg", " "+ _who +" "+ _what + "\n")
    print(get_servers_response())
    pass


def inbox():
    send_command("inbox"+"\n","")
    response = get_servers_response()
    print(response)
    len_msg = (len(response))
    x_msg = (response[6:len_msg])
    for i in range(int(x_msg)):
        print(read_one_line())
    time.sleep(1)
    pass

def get_users():
    send_command("users", "" + "\n")
    list_users = (get_servers_response().split())
    for i in list_users:
        print(i)
    pass

"""
The list of available actions that the user can perform
Each action is a dictionary with the following fields:
description: a textual description of the action
valid_states: a list specifying in which states this action is available
function: a function to call when the user chooses this particular action. The functions must be defined before
            the definition of this variable
"""


available_actions = [
    {
        "description": "Connect to a chat server",
        "valid_states": ["disconnected"],
        "function": connect_to_server
    },
    {
        "description": "Disconnect from the server",
        "valid_states": ["connected", "authorized"],
        "function": disconnect_from_server
    },
    {
        "description": "Authorize (log in)",
        "valid_states": ["connected", "authorized"],
        "function": client_login
    },
    {
        "description": "Send a public message",
        "valid_states": ["connected", "authorized"],
        "function": public_msg
    },
    {
        "description": "Send a private message",
        "valid_states": ["authorized"],
        "function": private_msg
    },
    {
        "description": "Read messages in the inbox",
        "valid_states": ["connected", "authorized"],
        "function": inbox
    },
    {
        "description": "See list of users",
        "valid_states": ["connected", "authorized"],
        "function": get_users
    },
    {
        "description": "Get a joke",
        "valid_states": ["connected", "authorized"],
        # TODO - optional step - implement the joke fetching from the server.
        # Hint: this part is not described in the protocol. But the command is simple. Try to find
        # out how it works ;)
        "function": None
    },
    {
        "description": "Quit the application",
        "valid_states": ["disconnected", "connected", "authorized"],
        "function": quit_application
    },
]


def run_chat_client():
    """ Run the chat client application loop. When this function exists, the application will stop """

    while must_run:
        print_menu()
        action = select_user_action()
        perform_user_action(action)
    print("Thanks for watching. Like and subscribe! 👍")


def print_menu():
    """ Print the menu showing the available options """
    print("==============================================")
    print("What do you want to do now? ")
    print("==============================================")
    print("Available options:")
    i = 1
    for a in available_actions:
        if current_state in a["valid_states"]:
            # Only hint about the action if the current state allows it
            print("  %i) %s" % (i, a["description"]))
        i += 1
    print()


def select_user_action():
    """
    Ask the user to choose and action by entering the index of the action
    :return: The action as an index in available_actions array or None if the input was invalid
    """
    number_of_actions = len(available_actions)
    hint = "Enter the number of your choice (1..%i):" % number_of_actions
    choice = input(hint)
    # Try to convert the input to an integer
    try:
        choice_int = int(choice)
    except ValueError:
        choice_int = -1

    if 1 <= choice_int <= number_of_actions:
        action = choice_int - 1
    else:
        action = None

    return action


def perform_user_action(action_index):
    """
    Perform the desired user action
    :param action_index: The index in available_actions array - the action to take
    :return: Desired state change as a string, None if no state change is needed
    """
    if action_index is not None:
        print()
        action = available_actions[action_index]
        if current_state in action["valid_states"]:
            function_to_run = available_actions[action_index]["function"]
            if function_to_run is not None:
                function_to_run()
            else:
                print("Internal error: NOT IMPLEMENTED (no function assigned for the action)!")
        else:
            print("This function is not allowed in the current system state (%s)" % current_state)
    else:
        print("Invalid input, please choose a valid action")
    print()
    return None

# Entrypoint for the application. In PyCharm you should see a green arrow on the left side.
# By clicking it you run the application.
if __name__ == '__main__':
    run_chat_client()