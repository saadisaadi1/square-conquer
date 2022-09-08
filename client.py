import pygame
import _thread
import socket

port = 55000
server = socket.gethostbyname(socket.gethostname())
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (server, port)
client.connect(server_address)
client.close()