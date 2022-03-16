import socket
import threading

# Connection data
host = '127.0.0.1'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists for Clients and Their Nicknames
clients = []
nicknames = []

# Sending Messages To All Connected Clients
def broadcast(message):
  for client in clients:
    client.send(message)

# Handling Messages from Clients
def handle(client):
	while True:
		try:
			# Broadcasting Message
			message = client.recv(1024)
			broadcast(message)
		except:
			# Removing and Closing Clients
			index = clients.index(client)
			clients.remove(client)
			client.close()
			nickname = nicknames[index]
			broadcast('{} left!'.format(nickname).encode('ascii'))
			nicknames.remove(nickname)
			break

# Receiving / Listening Function
def receive():
	while True:
		# Accept Connection
		client, address = server.accept()
		print("Connected with {}".format(str(address)))

		# Request And Store Nicknames
		client.send('NICK'.encode('ascii'))
		nickname = client.recv(1024).decode('ascii')
		if nickname == 'admin':
			client.send('PASS'.encode('ascii'))
			password = client.recv(1024).decode('ascii')

			if password != 'senki':
				client.send('REFUSE'.encode('ascii'))
				client.close()
				continue

		nicknames.append(nickname)
		clients.append(client)

		# Print And Broadcast Nickname
		print("Nickname is {}".format(nickname))
		broadcast("{} joined!".format(nickname).encode('ascii'))
		client.send('Connected to server!'.encode('ascii'))

		# Start Handling Thread for client
		thread = threading.Thread(target=handle, args=(client,))
		thread.start()

receive()
