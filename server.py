
import _thread
import socket

port = 55000
format = 'utf-8'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = socket.gethostbyname(socket.gethostname())
print(server_ip)
try:
    server.bind((server_ip, port))
except socket.error as e:
    print(str(e))
server.listen()
print("waiting for a connection...")
def threaded_client():
    pass

while True:
    conn, addr = server.accept()
    print(f"{addr} has connnected (o v o)")
    _thread.start_new_thread(threaded_client,())