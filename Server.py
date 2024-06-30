# **************************************
# Computer Networks and Internet 1 - 83455-01
# Server.py
# Itay Goldberg
# Yonatan Kupfer
# 1.1.23
# **************************************

import socket
import threading
from socket import socket, AF_INET, SOCK_STREAM

# The port number that the server will listen on
PORT = 5000
# The IP address of the server
HOST = '127.0.0.1'
# The encoding format for the messages sent between the client and server
FORMAT = "utf-8"
# A dictionary storing the group IDs as keys and the passwords for each group as values
group_users = {"0": []}
# A dictionary storing the group IDs as keys and lists of User objects as values
group_passwords = {"0": "password"}

# A class representing a user in the chat system
class User:
    def __init__(self, name, client_socket, client_address):
        self._name = name
        self._client_socket = client_socket
        self._client_address = client_address

def start_server():
    server_socket = socket(AF_INET, SOCK_STREAM)  # create a connection
    server_socket.bind((HOST, PORT))  # bind
    print("The server is running and ready to receive users")  # listening
    server_socket.listen()
    countGroup = 1000

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=client_handle, args=(client_socket, client_address, countGroup))
        client_thread.start()
        countGroup += 1

# function is responsible for handling the interactions between the client and the server.
# It sends an opening message to the client,
# The client's selection is then used to determine which action to take next.
# 1 - join an existing group chat by providing their name and the group's ID and password.
# 2 - create a new group chat by providing their name and a password for the group.
# 3 - disconnected from the server.
def client_handle(client_socket, client_address, countGroup):
    try:
        # sending an opening message to client
        opening_message = "Hello client, please choose an option:\n\t1. Connect to a group chat.\n\t2. Create a group chat.\n\t3. Exit the server."
        client_socket.send(opening_message.encode(FORMAT))
        while True:
            # switch case for the client option
            selected_option = client_socket.recv(1024).decode(FORMAT)
            exit_flag = 0
            if selected_option == "1":
                groupId, userName = join_existing_group(client_socket, client_address)
                exit_flag = handle_group_chat(client_socket, client_address, groupId, userName)
            elif selected_option == "2":
                groupId, userName = create_new_group(client_socket, client_address, countGroup)
                exit_flag = handle_group_chat(client_socket, client_address, groupId, userName)
            elif selected_option == "3":
                disconnect_from_server(client_socket, client_address)
                break
            else:
                client_socket.send("error, please insert valid number".encode(FORMAT))
            if exit_flag == -1:
                break
    except Exception as e:
        print(f"exception", {e})
        client_socket.close()
        return False

# function creates a new group and connects the client to it.
# It prompts the client to enter their name, creates a password for the group,
# and adds the client as a member of the group.
def create_new_group(client_socket, client_address, countGroup):
    name_message = "Enter your name:"
    client_socket.send(name_message.encode(FORMAT))
    name = client_socket.recv(1024).decode(FORMAT)

    password_message = "Create the chat's password:"
    client_socket.send(password_message.encode(FORMAT))
    password = client_socket.recv(1024).decode(FORMAT)

    groupId = countGroup
    countGroup = groupId + 1

    group_passwords[str(groupId)] = password
    newUser = User(name, client_socket, client_address)
    group_users[str(groupId)] = []
    group_users[str(groupId)].append(newUser)

    return groupId, newUser

# function connects the client to an existing group.
# It prompts the client to enter their name and the group ID,
# and then prompts the client to enter the group's password.
# If the group ID and password combination is incorrect,
# it gives the client a number of tries to enter the correct combination.
# If the client successfully enters the correct combination, it adds the client as a member of the group.
def join_existing_group(client_socket, client_address):
    numOfTries = 3
    name_message = "Enter your name:"
    client_socket.send(name_message.encode(FORMAT))
    name = client_socket.recv(1024).decode(FORMAT)

    groupId_message = "Enter group ID:"
    client_socket.send(groupId_message.encode(FORMAT))
    groupId = client_socket.recv(1024).decode(FORMAT)

    while numOfTries > 0:
        password_message = "Enter password:"
        client_socket.send(password_message.encode(FORMAT))
        password = client_socket.recv(1024).decode(FORMAT)
        if groupId not in group_passwords or group_passwords[groupId] != password:
            numOfTries -= 1
            client_socket.send((" * * Wrong Password * *\nYou have " + str(numOfTries) + " attempts left").encode(FORMAT))
        else:
            break

    if numOfTries == 0:
        client_socket.send(("The system exits").encode(FORMAT))
        disconnect_from_server(client_socket, client_address)
        return -1, "exit"

    newUser = User(name, client_socket, client_address)
    group_users[str(groupId)].append(newUser)
    connection_message = name + " connected to the group chat"
    # Sends a customized message to all chat members except the user who send
    for someome in group_users[str(groupId)]:
        if newUser != someome:
            someome._client_socket.send(connection_message.encode(FORMAT))
    return groupId, newUser

# Handles the communication and messaging for the specified group. Each user in the group
# will have their own thread executing this function.
def handle_group_chat(client_socket, client_address, groupId, user):
    client_socket.send(("Welcome to chat #" + str(groupId)+"\nYou can exit by sending the message: 'exit'").encode(FORMAT))
    while True:
        if user == "exit":
            break

        recieved = client_socket.recv(1024).decode(FORMAT)

        # when someone left, sends a customized message to all chat members and delete him from the group
        if recieved == "exit":
            client_socket.send(("Bye, Bye").encode(FORMAT))
            for someome in group_users[str(groupId)]:
                if user != someome:
                    someome._client_socket.send((" * * " + user._name + " left the group * *").encode(FORMAT))
            remove_client_from_group(groupId, user)
            disconnect_from_server(client_socket, client_address)
            break

        # Sends a customized message to all chat members
        message = user._name + ": " + recieved
        messageForU = "Me: " + recieved
        for someome in group_users[str(groupId)]:
            if user != someome:
                someome._client_socket.send(message.encode(FORMAT))
            else:
                someome._client_socket.send(messageForU.encode(FORMAT))
    return -1

# Removes the specified user from the list of users in the specified group
def remove_client_from_group(groupId, user):
    size = len(group_users[str(groupId)])
    for i in range(size):
        if group_users[str(groupId)][i] == user:
            group_users[str(groupId)].pop(i)
    return

def disconnect_from_server(client_socket, client_address):
    client_socket.close()
    return

if __name__ == "__main__":
    start_server()