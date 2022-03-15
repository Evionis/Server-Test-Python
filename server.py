"""
Creates a chat server that can communicate with many clients

Author: Noah Anderson
Class: CSI-275-02
Assignment: Final Project
Due Date: April 24, 2020 11:59 PM

Certification of Authenticity: I certify that this is entirely my own work,
except where I have given fully-documented references to the work of others.
I understand the definition and consequences of plagiarism and acknowledge
that the assessor of this assignment may, for the purpose of assessing this
assignment:
- Reproduce this assignment and provide a copy to another member of academic
- staff; and/or Communicate a copy of this assignment to a plagiarism checking
- service (which may then retain a copy of this assignment on its database for
- the purpose of future plagiarism checking)

Champlain College CSI-275, Spring 2020
The following code was written by Noah Anderson
(noah.anderson@mymail.champlain.edu)
"""

import threading
import socket
import json

# Users global variable
USERS = []


def communication_thread_work(connection):
    """Allow a thread receive messages from users and
    distribute them to their intended destinations."""
    exited = False
    while not exited:
        message = []
        # Get length of incoming message
        length = int.from_bytes(connection.recv(4), 'big')
        # Receive the message
        json_msg = connection.recv(length)
        json_decoded = json_msg.decode("utf-8")
        message = json.loads(json_decoded)
        # If the message is a private message
        if message[0] == "PRIVATE":
            for user in USERS:
                # Find the receiving user in the USERS list
                if message[3] == user[0]:
                    # Add length before message
                    json_msg = len(json_msg).to_bytes(4, 'big') + json_msg
                    # Send the message to that user
                    user[1].sendall(json_msg)
                    break
        # If the message is a broadcast message
        elif message[0] == "BROADCAST":
            # Add length before message
            json_msg = len(json_msg).to_bytes(4, 'big') + json_msg
            for user in USERS:
                # Send the message to every user
                user[1].sendall(json_msg)
        # If the message is an exit message
        else:
            for user in USERS:
                # Find the user in the USERS list
                if user[0] == message[1]:
                    # Remove the user from the USERS list
                    USERS.remove(user)
                    # Close the user's USERS socket
                    user[1].close()
                    break
            # Close the communication connection to the user
            connection.close()
            exited = True


def read_thread_work(read_sock):
    """Accept a connection and create a thread to handle it."""
    while True:
        # Accept a connection
        connection, address = read_sock.accept()
        # Create a new thread to handle the connection
        new_thread = threading.Thread(target=communication_thread_work,
                                      args=(connection,))
        # Start the new thread
        new_thread.start()


def write_thread_work(write_sock):
    """Accept a connection and add it to the USERS list."""
    while True:
        connection, address = write_sock.accept()
        # Get length of incoming message
        length = int.from_bytes(connection.recv(4), 'big')
        # Receive the message
        json_msg = connection.recv(length)
        json_msg = json_msg.decode("utf-8")
        message = json.loads(json_msg)
        # If the message is a start message
        if message[0] == "START":
            # Add the user's username and connection to the USERS list
            USERS.append((message[1], connection))
        # Ignore any other message
        else:
            pass


if __name__ == '__main__':
    # Create two sockets
    read_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    write_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the sockets
    read_socket.bind(("localhost", 5000))
    write_socket.bind(("localhost", 5001))

    # Set to listen
    read_socket.listen(50)
    write_socket.listen(50)

    # Set up the thread arguments
    read_args = (read_socket,)
    write_args = (write_socket,)

    # Create the threads and give them their arguments
    read_thread = threading.Thread(target=read_thread_work,
                                   args=read_args)
    write_thread = threading.Thread(target=write_thread_work,
                                    args=write_args)

    # Start the threads
    read_thread.start()
    write_thread.start()

    # Make the main program wait for all of the threads
    # to finish before continuing
    read_thread.join()
    write_thread.join()