import socket
import threading
import json
import xml.etree.ElementTree as ET
from cryptography.fernet import Fernet
import pickle

server_files_path = "C:/Users/lhps1/OneDrive/Máy tính/Module 2 End Assignment/server/file"

HEADER = 64
PORT = 7991
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def start():
    server.listen()
    print(f"[LISTENTING] The current server is {SERVER}")
    conn, addr = server.accept()
    thread = threading.Thread(target = handle_client, args = (conn, addr))
    thread.start()
    print(f"[ACTIVE] {threading.active_count() - 1}")

def deserialize_data(data, serialization_format):
    if serialization_format == "binary":
        return pickle.loads(data)
    elif serialization_format == "json":
        return json.loads(data.decode())
    elif serialization_format == "xml":
        root = ET.fromstring(data.decode("utf-8"))
        data_dict = {}
        for element in root:
            data_dict[element.tag] = element.text
        return data_dict
    else:
        raise ValueError("Invalid serialization format")

def receive_file(conn):
    print("[SERVER] Connection made!")
    key = b'6WkZxGZxaFNba2sPXg8mbIgXxhjdw1iIo6DgymmqT_Q='
    cipher_suite = Fernet(key)
    file_content = b""
    try:
        serialization_format = conn.recv(1024).decode(FORMAT)
        data = conn.recv(1024)
        received_dict = deserialize_data(data, serialization_format)
        filesize = int(conn.recv(1024).decode(FORMAT).strip())
        filename = conn.recv(1024).decode(FORMAT)
        print(f"Files in {serialization_format} format: {received_dict}")
        while filesize > 0:
            data = conn.recv(min(filesize, 1024))
            file_content += data
            filesize -= len(data)

        decrytion = cipher_suite.decrypt(file_content)
        with open(filename, "wb") as files:
            files.write(decrytion)

        manual_input = input("Opening file? (Y/N): ")
        if manual_input.lower().strip() == 'Y' and decrytion:
            try:
                print("File content: ")
                print(decrytion.decode(FORMAT))
            except UnicodeDecodeError:
                print("Cannot decode binary file to text.")
        elif not decrytion:
            print("File is empty.")
        elif manual_input.lower().strip() == 'N':
            conn.close()
    except ValueError as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def handle_client(conn, addr):
   print(f"[NEWCONNECTION] {addr} connect.")
   connected = True
   while connected:
       msg_length = conn.recv(HEADER).decode(FORMAT)
       if msg_length:
           msg_length = int(msg_length)
           msg = conn.recv(msg_length).decode(FORMAT)
           if msg.startswith("!SENDFILE"):
               print("[SERVER] File recognized!")
               receive_file(conn)   
           elif msg == DISCONNECT_MSG:
               connected = False
               print("No connection made")
           else:
               print(msg)
       else: 
           print("error")

print("[STARTING] server is starting...")
start()