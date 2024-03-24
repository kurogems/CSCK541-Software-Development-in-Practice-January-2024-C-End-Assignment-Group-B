import socket
import os
import json
import xml.etree.ElementTree as ET
from cryptography.fernet import Fernet
import pickle

file_path = "C:/Users/lhps1/OneDrive/Máy tính/Module 2 End Assignment/client/files"

HEADER = 64
PORT = 7991
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
data_dict = {'name': 'Group B', 'module': 'Data Science', 'location': 'Global'}

def send(msg):
    msg = msg.encode(FORMAT)
    msg_length = len(msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(msg)
    if msg != DISCONNECT_MSG.encode(FORMAT):
        print(client.recv(1024).decode(FORMAT))

def serialize_dict(data_dict, serialization_format):
    if serialization_format == "binary":
        return pickle.dumps(data_dict)
    elif serialization_format == "json":
        return json.dumps(data_dict).encode(FORMAT)
    elif serialization_format == "xml":
        root = ET.Element("data")
        for key, value in data_dict.items():
            element = ET.SubElement(root, key)
            element.text = str(value)
        return ET.tostring(root, encoding=FORMAT)
    else:
        raise ValueError("Invalid serialization format")
    
def send_file(filename):
    key = b'6WkZxGZxaFNba2sPXg8mbIgXxhjdw1iIo6DgymmqT_Q='
    cipher_suite = Fernet(key)
    filelocation = os.path.join(file_path, filename)
    if os.path.exists(file_path) and os.path.isfile(filelocation):
        send(f"!SENDFILE {filename}")
        serialization_format = input("Enter serialization format (binary/json/xml): ").lower()
        serialized_data = serialize_dict(data_dict, serialization_format)
        client.sendall(serialization_format.ljust(1024).encode())
        client.sendall(serialized_data)
    
        with open(filename, "rb") as file:
            encrypted_file_data = cipher_suite.encrypt(file.read())
        print("[CLIENT] Sending file...")
        encrypted_file_size = len(encrypted_file_data)
        client.sendall(filename.ljust(1024).encode())
        client.sendall(str(encrypted_file_size).ljust(1024).encode())
        client.sendall(encrypted_file_data)

        print("[CLIENT] File sent successfully")
    else:
        print("File not found.")
    client.close()   

send("hello world")

#send(DISCONNECT_MSG)
    
send_file("example.txt")