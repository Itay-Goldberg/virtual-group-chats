# **************************************
# Computer Networks and Internet 1 - 83455-01
# Client.py
# Itay Goldberg
# Yonatan Kupfer
# 1.1.23
# **************************************

import socket
import threading
from PyQt5 import QtWidgets, QtGui

# The port number that the server will listen on
PORT = 5000
# The IP address of the server
HOST = '127.0.0.1'
# The encoding format for the messages sent between the client and server
FORMAT = "utf-8"

# This class is for the client's GUI.
# It has a message input field, a send button, and a conversation display area.
# Has a method for sending messages to the server and another for receiving messages from the server.
class ClientWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client_socket.connect((HOST,PORT))
        self.init_ui()
        self.receive_thread = threading.Thread(target = self.receive)
        self.receive_thread.start()

    # Sets up the layout and appearance of the client window.
    def init_ui(self):
        self.setWindowTitle("Itay & Yonatan - Group Chat App")
        self.setGeometry(70, 70, 600, 750)
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        self.message_input = QtWidgets.QLineEdit(self)
        self.message_input.setPlaceholderText("Write here")
        self.message_input.returnPressed.connect(self.send_message)

        # Set the font size of the message input field to 12 points
        font = QtGui.QFont()
        font.setPointSize(12)
        self.message_input.setFont(font)

        self.send_button = QtWidgets.QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)

        # Set the font size of the message input field to 10 points
        font = QtGui.QFont()
        font.setPointSize(10)
        self.send_button.setFont(font)

        self.conversation_display = QtWidgets.QTextEdit(self)
        self.conversation_display.setReadOnly(True)

        # Set the font size of the conversation display area to 16 points
        self.conversation_display.setFont(font)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.conversation_display)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        self.setLayout(layout)
        self.show()

    # called when the send button is clicked or when the user
    # hits the "enter" key while typing in the message input field.
    # It sends the message to the server.
    def send_message(self):
        message = self.message_input.text()
        self.client_socket.send(message.encode(FORMAT))
        self.message_input.clear()

    # a thread that continuously receives messages from the server and displays them in the conversation display area.
    def receive(self):
        while True:
            message = self.client_socket.recv(1024).decode(FORMAT)
            self.conversation_display.append(message)

# creates a client socket and starts two threads, one for sending and one for receiving messages.
def start_client():
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((HOST,PORT))
    try:
        receive_thread = threading.Thread(target = ClientWindow.receive,args = (client_socket,client_socket))
        receive_thread.start()
        send_thread = threading.Thread(target = ClientWindow.send, args = (client_socket,client_socket))
        send_thread.start()
    except Exception as e:
        print(f"exception", {e})
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = ClientWindow()
    app.exec_()
    start_client()