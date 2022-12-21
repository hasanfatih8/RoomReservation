import socket
import os.path

HOST = "127.0.0.1"
PORT = 9999
# with command, we don't need to use try catch blocks

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 

    s.bind((HOST, PORT)) 
    s.listen() # if you put any number in this function ex: 5, it means that it will listen 5 connections after that it is going to throw an error
    conn, addr = s.accept() #connection object will be stored in conn, list of ip addresses will be storedin addr
    with conn:
        print(f"Connected by {addr}")
        while True:

            data = conn.recv(1024) # take the first 1024 byte, other than that can be junk
            if not data:
                break
            url= data.decode("utf-8")
            print("The url is", url)

            funcType= url.split("?")[0]
            name=url.split("?")[1].split("=")[1]
            
            if funcType == "/add":
                control = 0
                if os.path.exists('rooms.txt'):
                    lines = []
                    file = open("rooms.txt", 'r')                      
                    for line in file:
                        if(name == line.strip()):
                            print("The room name is already exist 403 atilcak")
                            control = 1
                            file.close()
                            break
                
                if(control == 0):
                    file = open("rooms.txt", 'a')                   
                    file.write(name)
                    file.write("\n")
                    print("The room name is added to the file")
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
                        print("The room name is  not exist")
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
                    print("file not exists")

                
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
                        print("invalid input 400 atilcak ROOM YOK ROOMS TXT DE")
                    else:
                        if(roomname == "" or int(day)>7 or int(day)<0 or int(hour)<9 or int(hour)+duration-1>17): #invalid input check
                            print("invalid input 400 atilcak")
                        else:
                            control = 0 #if room already reserved sets to 1
                            if os.path.exists('reservations.txt'):
                                reservationFileRead = open("reservations.txt", "r")
                                for line in reservationFileRead:
                                    elements = line.split(" ")
                                    if(elements[0] == roomname and elements[1] == day):
                                        hoursLength = len(elements) - 2                       
                                        
                                        for i in range(0,hoursLength): #if starting hour of new reservation matches with other reservation                                                   
                                            if(elements[i + 2].strip() == hour):
                                                control = 1     
                                                break
                                        
                                        for j in range(0,hoursLength): #if end hour of new reservation matches with other reservation                                                                            
                                            if(elements[j + 2].strip() == str(int(hour) + duration - 1)):
                                                control = 1     
                                                break
                                    if(control == 1):
                                        break
                                reservationFileRead.close()
                            if(control == 1):
                                print("already reserved 403 atilcak")
                            else:    
                                reservationFile = open("reservations.txt", "a+")
                                reservation = (roomname + " " + day +  " " + hour + " ")
                                reservationFile.write(reservation)
                                for i in range(1,duration):
                                    hours = int(hour) + i                 
                                    reservationFile.write(str(hours))
                                    reservationFile.write(" ")
                                reservationFile.write("\n")                    
                                reservationFile.close()
                else:
                    print("rooms file not exists")    
            
            elif funcType == "/checkavailability":
                if os.path.exists('reservations.txt') or os.path.exists('rooms.txt'):
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
                        print("room not found 404 atilcak ROOM YOK ROOMS TXT DE")
                    else:
                        if(int(day)>7 or int(day)<0): #invalid input check
                            print("invalid input 400 atilcak")
                        else:
                            reservationFile = open("reservations.txt", "r")
                            for line in reservationFile:    # finds reserved hours
                                elements = line.split(" ")
                                if(elements[0] == roomname and elements[1] == day):
                                    hoursLength = len(elements) - 2                                                  
                                    for i in range(0,hoursLength):                                                   
                                        reservedHours.append(elements[i + 2].strip())
                            reservationFile.close()
                            availableHours = []  
                            for i in range(0,9):    # finds available hours
                                if(str(i+9) not in reservedHours):
                                    availableHours.append(i+9)
                            print("available hours: ", availableHours)
                else:
                    print("rooms or reservations file not exists")


                
                #/checkavailability?name=roomname&day=x:
            # Unlike send(), this method continues to send data from bytes until either all data has been sent or an error occurs.
            # None is returned on success.
            conn.sendall(data)
