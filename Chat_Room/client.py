import socket
import select
import msvcrt

name = input("Enter your name: ")

client_side = socket.socket()
client_side.connect(('127.0.0.1', 8200))

data = f"{len(name)},{name},0"
client_side.send(data.encode())
response = client_side.recv(1024).decode()
while response.startswith("Try"):
    name = input("Enter a different name: ")
    data = f"{len(name)},{name},0"
    client_side.send(data.encode())
    response = client_side.recv(1024).decode()

inp = ""

while inp != "quit":
    
    rList, wList, xList = select.select([client_side], [client_side], [])
    for sock in rList:
        data = sock.recv(1024).decode()
        print(data)
        if data == "You were kicked from the chat!":
            inp = "quit"

    if msvcrt.kbhit():
        key_pressed = msvcrt.getch()
        key_pressed = key_pressed.decode()
        print(key_pressed, end="")
    
        if key_pressed == "\r":
            command = '1'

            if inp.startswith("inviteMan"):
                command = '2'
                inp = inp.replace("inviteMan ", "")

            elif inp.startswith("getout"):
                command = '3'
                inp = inp.replace("getout ", "")

            elif inp.startswith("sh"):
                command = '4'
                inp = inp.split(' ')[-1]

            elif inp.startswith("view-managers"):
                command = '5'
                inp = ""

            print("\n")
            data = f"{len(name)},{name},{command},{len(inp)},{inp}"
            client_side.send(data.encode())
            inp = ""
        else:
            if key_pressed == "\x08":
                inp = inp[0:-1]
            else:
                inp += key_pressed
            
        if inp == 'quit':
            data = f"{len(name)},{name},1,{inp}"
            client_side.send(data.encode())

client_side.close()
