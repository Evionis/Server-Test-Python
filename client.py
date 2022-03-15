"""
Creates a client that can communicate with a chat server

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


def create_username():
    """Allow a user to create a username and return it."""
    print("Input your username (alphanumeric only, no spaces): ")
    while True:
        # Create a username
        uname = input()
        # Check that it is alphanumeric
        if uname.isalnum():
            break
        else:
            print("Unacceptable username.")
    return uname


def send_thread_work(send_sock, uname):
    """Process messages from the user into json lists and
     send them to the server"""
    exited = False
    while not exited:
        message = []
        split_message = []
        # Get the message from the user
        text = input()
        # If the message is a private message
        if text[0] == "@":
            split_message = text.split(' ', 1)
            # Structure: PRIVATE, username, message, receiving user
            message.append("PRIVATE")
            message.append(uname)
            message.append(split_message[1])
            message.append(split_message[0][1:])
        # If the message is an exit message
        elif text[0] == "!":
            # Structure: EXIT, username
            message.append("EXIT")
            message.append(uname)
            exited = True
        # If the message is a broadcast message
        else:
            # Structure: BROADCAST, username, message
            message.append("BROADCAST")
            message.append(uname)
            message.append(text)
        json_msg = json.dumps(message)
        # Add length before message
        json_msg = len(json_msg).to_bytes(4, 'big') + json_msg.encode("utf-8")
        # Send to server
        send_sock.sendall(json_msg)
        # If last message was an exit message, close the socket
        if exited:
            send_sock.close()
            print("Exited")


def recv_thread_work(recv_sock, uname):
    """Process messages from the server into messages and
    print them to the console"""
    message = []
    json_msg = json.dumps(["START", uname])
    # Add length before message
    json_msg = len(json_msg).to_bytes(4, 'big') + json_msg.encode("utf-8")
    # Send start message to server
    recv_sock.sendall(json_msg)
    while True:
        # Get length of incoming message
        length = int.from_bytes(recv_sock.recv(4), 'big')
        # Break if nothing was received
        if not length:
            break
        else:
            # Get message
            json_msg = recv_sock.recv(length)
            json_msg = json_msg.decode("utf-8")
            message = json.loads(json_msg)
            # Format private message
            if message[0] == "PRIVATE":
                print(message[1] + " (private): " + message[2])
            # Format broadcast message
            else:
                print(message[1] + ": " + message[2])


if __name__ == '__main__':
    # Create username
    uname = create_username()
    # Create two sockets
    recv_socket = socket.socket()
    send_socket = socket.socket()

    # Connect the sockets
    recv_socket.connect(("localhost", 5001))
    send_socket.connect(("localhost", 5000))

    # Set up the thread arguments
    recv_args = (recv_socket, uname)
    send_args = (send_socket, uname)

    # Create the threads and give them their arguments
    recv_thread = threading.Thread(target=recv_thread_work,
                                   args=recv_args)
    send_thread = threading.Thread(target=send_thread_work,
                                   args=send_args)

    # Start the threads
    recv_thread.start()
    send_thread.start()

    # Make the main program wait for all of the threads
    # to finish before continuing
    recv_thread.join()
    send_thread.join()
