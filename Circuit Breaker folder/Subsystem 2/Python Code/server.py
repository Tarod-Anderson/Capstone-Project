#!/usr/bin/env python3
import socket
import os

HOST = "10.42.0.1"
PORT = 5001

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)

print(f"[SERVER] Listening on {HOST}:{PORT}...")

while True:
	conn, addr = s.accept()
	print(f"[SERVER] Connection from {addr}")

	filename = conn.recv(1024).decode()
	print(f"[SERVER] Receiving file: {filename}")
	conn.send(b"OK-FILESIZE")

	raw = conn.recv(1024).decode().strip()
	if not raw:
		raise ValueError("Empty filesize received")
	filesize = int(raw)
	print(f"[SERVER] File Size: {filesize} bytes")
	conn.send(b"OK-FILESIZE")

	with open(filename, "wb") as f:
		received = 0
		while received < filesize:
			data = conn.recv(4096)
			if not data:
				break
			f.write(data)
			received += len(data)

	print(f"[SERVER] File '{filename}' received successfully.\n")
	conn.close()
