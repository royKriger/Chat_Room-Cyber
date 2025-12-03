import socket
import select
from datetime import datetime

open_sockets = []
online_users = []
admins = []
silenced = []

server_side = socket.socket()
server_side.bind(('0.0.0.0', 8200))
server_side.listen()

while True:
    all_sock = [server_side] + open_sockets
    rList, wList, xList = select.select(all_sock, all_sock, [])
    for sock in rList:
        message = ""
        if sock == server_side:
            client_side, addr = server_side.accept()
            open_sockets.append(client_side)
        else:
            data = sock.recv(1024).decode()
            data = data.split(',')
            print(data)
            
            name = data[1]
            if data[2] == '0':
                if name in online_users:
                    sock.send("Try another name this one is taken!".encode())
                else:
                    message = f"The user {name} was connected"
                    online_users.append(name)
                    if len(open_sockets) == 1:
                        admins.append(name)
                
            elif data[2] == '1':
                if data[-1] == 'quit':
                    message = f"{datetime.now().strftime("%H:%M")} {name} has left the chat!"
                    if name in admins:
                        admins.remove(name)
                    open_sockets.remove(sock)
                    online_users.remove(name)
                    if (not admins) and online_users:
                            admins.append(online_users[0])
                    sock.close()
                else:
                    if name in admins:
                        name = f"@{name}"
                    if name.replace('@', '') in silenced:
                        sock.send("You are silenced!".encode())
                    elif data[-1].startswith('!'):
                        receiver = data[-1].split()[0]
                        data[-1] = data[-1].split()[1:]
                        i = online_users.index(receiver[1:])
                        data = f"{datetime.now().strftime("%H:%M")} !{name}: {' '.join(data[-1])}"
                        open_sockets[i].send(data.encode())
                    else:
                        message = f"{datetime.now().strftime("%H:%M")} {name}: {data[-1]}"
                    name = name.replace("@", "")
             
            elif data[2] == '2':
                if name in admins:
                    admins.append(data[-1])
                else:
                    sock.send("You do not have the authority to do this!".encode())
                
            elif data[2] == '3':
                if name in admins:
                    remove = online_users.index(data[-1])
                    remove_sock = open_sockets[remove]
                    cur = online_users[remove]
                    online_users.remove(online_users[remove])
                    remove_sock.send("You were kicked from the chat!".encode())
                    open_sockets.remove(remove_sock)
                    remove_sock.close()
                    if cur in admins:
                        admins.remove(cur)
                    if (not admins) and online_users:
                            admins.append(online_users[0])
                else:
                    sock.send("You do not have the authority to do this!".encode())

            elif data[2] == '4':
                if name in admins:
                    if data[-1] in silenced:
                        silenced.remove(data[-1])
                    else:
                        silenced.append(data[-1])
                else:
                    sock.send("You do not have the authority to do this!".encode())

            else:
                data = f"The admins are: {','.join(admins)}"
                sock.send(data.encode())

            for socket in open_sockets:
                socket.send(message.encode())

server_side.close()
