import socket
import os

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
    command = input("Write a command: ")
    s.send(command.encode())
    if command.strip().upper() == "STOP":
        break

    chunk = s.recv(4096)

    # Controlla se è un file
    if chunk.startswith(b"FILENAME:"):
        header, file_data = chunk.split(b"\n", 1)
        filename = header.decode().split(":", 1)[1].strip()
        filepath = os.path.join(folder_path, filename)
        print(f"File received: {filename}, saved in {filepath}")

        # Scrivo il file in modalità binaria
        with open(filepath, "wb") as f:
            f.write(file_data)

    else:
        text = chunk.decode(errors="replace")
        print(text)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print("Textual output saved.")

s.close()
