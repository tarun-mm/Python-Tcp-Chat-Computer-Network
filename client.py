import socket
import threading

# Choosing Nickname
nickname = input("Choose your nickname: ")
if nickname == 'admin':
  password = input("Enter password for admin: ")

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 55555))

stop_thread = False

# Listening to Server and Sending Nickname
def receive():
  while True:
    global stop_thread
    if stop_thread:
      break
    try:
      # Receive Message From Server
      # If 'NICK' Send Nickname
      message = client.recv(1024).decode("ascii")
      if message == "NICK":
        client.send(nickname.encode("ascii"))
        next_message = client.recv(1024).decode('ascii')
        if next_message == 'PASS':
          client.send(password.encode('ascii'))
          if client.recv(1024).decode('ascii') == 'REFUSE':
            print("Connection was refused! Wrong password.")
            stop_thread = True
      else:
        print(message)
    except:
      # Close Connection When Error
      print("An error occured!")
      client.close()
      break

# Sending Messages To Server
def write():
  while True:
    if stop_thread:
      break
    message = '{}: {}'.format(nickname, input(''))
    if message[len(nickname)+2:].startswith('/'):
      if nickname == 'admin':
        if message[len(nickname)+2:].startswith('/kick'):
          client.send('KICK {}'.format(message[len(nickname)+2+6:]).encode('ascii'))
        elif message[len(nickname)+2:].startswith('/ban'):
          client.send('BAN {}'.format(message[len(nickname)+2+5:]).encode('ascii'))
      else:
        print("Commands can only be executed by the admin!")
    else:
      client.send(message.encode('ascii'))

# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()