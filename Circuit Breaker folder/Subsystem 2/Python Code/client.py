#!/usr/bin/env python3
import socket
import os

SERVER_IP = "10.42.0.1"
PORT = 5001
FILE_TO_SEND = "diag.mp4"

s = socket.socket()
s.connect((SERVER_IP, PORT))
print(f"[CLIENT] Connected to {SERVER_IP}:{PORT}")

s.send(FILE_TO_SEND.encode())
s.recv(1024)

filesize = os.path.getsize(FILE_TO_SEND)
s.send(str(filesize).encode())
s.recv(1024)

with open(FILE_TO_SEND, "rb") as f:
	data = f.read(4096)
	while data:
		s.send(data)
		data = f.read(4096)

print("[CLIENT] File sent.")
s.close()
