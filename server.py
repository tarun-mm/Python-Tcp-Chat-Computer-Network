import socket
import threading

# Connection data
host = '127.0.0.1'
port = 55556

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
			msg = message = client.recv(1024)
			if msg.decode('ascii').startswith('KICK'):
				if nicknames[clients.index(client)] == 'admin':
					name_to_kick = msg.decode('ascii')[5:]
					kick_user(name_to_kick)
				else:
					client.send('Command was refused!'.encode('ascii'))
			elif msg.decode('ascii').startswith('BAN'):
				if nicknames[clients.index(client)] == 'admin':
					name_to_ban = msg.decode('ascii')[4:]
					kick_user(name_to_ban)
					with open('bans.txt', 'a') as f:
						f.write('{}\n'.format(name_to_ban))
					print('{} was banned.'.format(name_to_ban))
				else:
					client.send('Command was refused!'.encode('ascii'))
			else:
				broadcast(message)
		except:
			# Removing and Closing Clients
			if client in clients:
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
		with open('bans.txt', 'r') as f:
			bans = f.readlines()
		
		if nickname+'\n' in bans:
			client.send('BAN'.encode('ascii'))
			client.close()
			continue


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

def kick_user(name):
	if name in nicknames:
		name_index = nicknames.index(name)
		client_to_kick = clients[name_index]
		clients.remove(client_to_kick)
		client_to_kick.send('You were kicked by an admin!'.encode('ascii'))
		client_to_kick.close()
		nicknames.remove(name)
		broadcast('{} was kicked by an admin!'.format(name).encode('ascii'))

print('Server is running...')
receive()
