import socket
import os.path

HOST = "localhost"
PORT = 8081
# with command, we don't need to use try catch blocks

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 

    s.bind((HOST, PORT)) 
    s.listen() # if you put any number in this function ex: 5, it means that it will listen 5 connections after that it is going to throw an error
    while True:
        conn, addr = s.accept() #connection object will be stored in conn, list of ip addresses will be storedin addr

        with conn:
            print(f"Connected by {addr}")
           

            data = conn.recv(1024) # take the first 1024 byte, other than that can be junk
            if not data:
                break
            url= data.decode("utf-8")
            print("The url is", url)

            funcType= url.split("?")[0]
            print("The functype is", funcType)

            name=url.split("?")[1].split("=")[1] # [0] = name , [1] = roomname&day , [2] = 8
            print("The name is", name)


            if funcType == "/add":
                isExists = 0
                if os.path.exists('rooms.txt'):
                    lines = []
                    file = open("rooms.txt", 'r')                      
                    for line in file:
                        if(name == line.strip()):
                            #print("The room name is already exist 403 atilcak")
                            conn.sendall(b"HTTP/1.1 403 Forbidden\n")
                            isExists = 1
                            file.close()
                            break
                        
                if(isExists == 0):
                    file = open("rooms.txt", 'a')                   
                    file.write(name)
                    file.write("\n")
                    #print("The room name is added to the file")
                    conn.sendall(
                        b"HTTP/1.1 200 OK\n" +
                        b"Content-Type: text/html\n" +
                        b"\n")
                    file.close()
            elif funcType == "/remove":
                if os.path.exists('rooms.txt'):
                    lines = []
                    file = open("rooms.txt", 'r')
                    for line in file:
                        lines.append(line.strip())
                    file.close()
                    for line in lines:
                        print(line)
                    if not lines.__contains__(name):
                        #print("The room name is  not exist")
                        conn.sendall(b"HTTP/1.1 404 Not Found\n")
                    else:
                        print("The room name is  exist")                                        
                        file = open("rooms.txt", 'w')
                        file.seek(0)
                        lines.remove(name)
                        for line in lines:                                                     
                            file.write(line)
                            file.write("\n")
                        file.close()
                    #    with open("ids.txt", "r") as f:
                    #    lines = f.readlines()   
                    #    with open("ids.txt", "w") as f:
                    #    for line in lines:
                    #        if line.strip("\n") != "hasan":
                    #            f.write(line)
                    #
                else:
                    #print("file not exists")
                    conn.sendall(b"HTTP/1.1 404 Not Found\n")
            elif funcType == "/reserve":
                if os.path.exists('rooms.txt'):    
                    roomname = name.split("&")[0]
                    endpoints = url.split("?")[1]
                    day = endpoints.split("&")[1].split("=")[1]
                    hour = endpoints.split("&")[2].split("=")[1]
                    duration = int(endpoints.split("&")[3].split("=")[1])
                    controlForRoom = 0
                    rooms = open("rooms.txt", 'r')    
                    for line in rooms:  # checks whether room exists or not BU LAZIM MI EMİN DEĞİLİM
                        if line.strip() == roomname:
                            controlForRoom = 1
                            break
                    rooms.close()
                    if(controlForRoom == 0):   
                        conn.sendall(b"HTTP/1.1 404 Not Found\n")
                    else:
                        if(roomname == "" or int(day)>7 or int(day)<0 or int(hour)<9 or int(hour)+duration-1>17): #invalid input check
                            print("invalid input 400 atilcak")
                            conn.sendall(b"HTTP/1.1 400 Bad Request\n")
                        else:
                            isReserved = 0 #if room already reserved sets to 1
                            if os.path.exists('reservations.txt'):
                                reservationFileRead = open("reservations.txt", "r")
                                for line in reservationFileRead:
                                    elements = line.split(" ")
                                    if(elements[1] == roomname and elements[3] == day):
                                        hoursLength = len(elements) - 4                       

                                        for i in range(0,hoursLength): #if starting hour of new reservation matches with other reservation                                                   
                                            if(elements[i + 4].strip() == hour):
                                                isReserved = 1     
                                                break

                                        for j in range(0,hoursLength): #if end hour of new reservation matches with other reservation                                                                            
                                            if(elements[j + 4].strip() == str(int(hour) + duration - 1)):
                                                isReserved = 1     
                                                break
                                    if(isReserved == 1):
                                        break
                                reservationFileRead.close()
                            if(isReserved == 1):
                                print("already reserved 403 atilcak")
                                conn.sendall(b"HTTP/1.1 403 Forbidden\n")
                            else:
                                conn.sendall(
                                    b"HTTP/1.1 200 OK\n" +
                                    b"Content-Type: text/html\n" +
                                    b"\n")
                            
                else:
                    conn.sendall(b"HTTP/1.1 404 Not Found\n")    
            elif funcType == "/checkavailability":
                if os.path.exists('rooms.txt'):
                    roomname = name.split("&")[0]
                    endpoints = url.split("?")[1]
                    day = endpoints.split("&")[1].split("=")[1]
                    reservedHours = []
                    controlForRoom = 0
                    rooms = open("rooms.txt", 'r')
                    for line in rooms:  # checks whether room exists or not
                        if line.strip() == roomname:
                            controlForRoom = 1
                            break
                    rooms.close()
                    if(controlForRoom == 0):
                        #print("room not found 404 atilcak ROOM YOK ROOMS TXT DE")
                        conn.sendall(b"HTTP/1.1 404 Not Found\n")
                    else:
                        if(int(day)>7 or int(day)<0): #invalid input check
                           # print("invalid input for day number /// 400 atilcak")
                            conn.sendall(b"HTTP/1.1 400 Bad Request\n")
                        else:
                            if os.path.exists('reservations.txt'):
                                roomsFile = open("reservations.txt", "r")
                                for line in roomsFile:    # finds reserved hours
                                    elements = line.split(" ")
                                    if(elements[0] == roomname and elements[1] == day):
                                        hoursLength = len(elements) - 2
                                        for i in range(0,hoursLength):
                                            reservedHours.append(elements[i + 2].strip())
                                roomsFile.close()
                                availableHours = []
                                availableHoursReturn = ""
                                for i in range(0,9):    # finds available hours
                                    if(str(i+9) not in reservedHours):
                                        availableHours.append(i+9)

                                for i in availableHours:
                                    availableHoursReturn += str(i) + " "

                                conn.sendall(b"HTTP/1.1 200 OK\n" 
                                             b"Content-Type: text/html\n" 
                                             b"\n" + availableHoursReturn.encode()) 
                                print("available hours: ", availableHours)
                            else:
                                conn.sendall(b"HTTP/1.1 400 Bad Request\n")
            elif funcType == "/get": #listavailability?room=roomname
                print("-------get request to room server-------")
                
                
                
                print ("Reservation server want to get information about room: ",name)
                rooms = open("rooms.txt", 'r')
                isExist=False
                for line in rooms:
                    if line.strip() == name:
                        print("The room name is exist")
                        #roomInfo = line.strip() + " " 
                        isExist=True                       
                        break
                if isExist==False:
                    print("The room name is not exist")
                    conn.sendall(b"HTTP/1.1 404 Not Found\n")
                else:
                    conn.sendall(b"HTTP/1.1 200 OK\n" +
                                 b"Content-Type: text/html\n" +
                                 b"\n" +
                                 b"Room name: " + name.encode() )
            else:
                conn.sendall(b"HTTP/1.1 400 Bad Request\n")


