import socket
import os.path

from splitOperations import *

HOST = "localhost"
PORT = 8081


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
            # Check if the request is for the favicon
            if b"favicon.ico" in data:
            # Ignore the request and do not send a response
                pass
            url= data.decode("utf-8")
            print("The url is", url)
          
            requestLine,funcType,name=splitURL(url)           

            if funcType == "/add":
                isExists = 0
                if os.path.exists('rooms.txt'):
                    lines = []
                    file = open("rooms.txt", 'r')                      
                    for line in file:
                        if(name == line.strip()):                                                        
                            response = responseFormatter("400 Bad Request", "Room Added", f"Room {name} is already exist")              
                            conn.sendall(response)
                            isExists = 1
                            file.close()
                            break
                        
                if(isExists == 0):
                    file = open("rooms.txt", 'a')                   
                    file.write(name)
                    file.write("\n")

                    response = responseFormatter("200 OK", "Room Added", f"Room {name} is added")    
                    conn.sendall(response)

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

                        response = responseFormatter("404 Not Found", "title", f"Room {name} does not exist")
                        conn.sendall(response)
                    else:
                        print("The room name is  exist")                                        
                        file = open("rooms.txt", 'w')
                        file.seek(0)
                        lines.remove(name)
                        for line in lines:                                                     
                            file.write(line)
                            file.write("\n")
                        file.close()

                        response = responseFormatter("200 OK", "title", f"Room {name} is removed")             
                        conn.sendall(response)
                else:
                    response = responseFormatter("404 Not Found", "title", f"Room {name} is not exist")
                    conn.sendall(response)
            elif funcType == "/reserve":
                if os.path.exists('rooms.txt'):  
                    
                    roomname = name.split("&")[0].strip()
                    endpoints = requestLine.split("?")[1]
                    day = endpoints.split("&")[1].split("=")[1].strip()
                    hour = endpoints.split("&")[2].split("=")[1].strip ()
                    duration = int(endpoints.split("&")[3].split("=")[1].strip())

                    print("roomname",roomname,"day",day,"hour",hour,"duration",duration)
                    controlForRoom = 0
                    rooms = open("rooms.txt", 'r')    
                    for line in rooms:  # checks whether room exists or not BU LAZIM MI EMİN DEĞİLİM
                        print("line",line,"roomname",roomname)
                        if line.strip() == roomname:
                            controlForRoom = 1
                            break
                    rooms.close()

                    print("controlForRoom",controlForRoom)
                    if(controlForRoom == 0):   
                        response = responseFormatter("404 Not Found", "title", f"Room {roomname} does not exist")
                        conn.sendall(response)
                    else:
                        if(roomname == "" or int(day)>7 or int(day)<0 or int(hour)<9 or int(hour)+duration-1>17): #invalid input check
                            print("invalid input 400 atilcak")
                            
                            response = responseFormatter("400 Bad Request", "Invalid Input", "Invalid input")
                            conn.sendall(response)
                        else:
                            isReserved = 0 #if room already reserved sets to 1
                            if os.path.exists('reservations.txt'):
                                print("reservations.txt exists")
                                reservationFileRead = open("reservations.txt", "r")


                                for line in reservationFileRead:
                                    print("line",line)
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

                                

                            print("isReserved",isReserved)
                            if(isReserved == 1):
                                print("already reserved 403 atilcak")
                                response = responseFormatter("403 Forbidden", "Already reserved", f"Room {roomname} is already reserved")
                                conn.sendall(response)
                            else:
                                print("reserved 200 atilcak")
                                response = responseFormatter("200 OK", "Reservation Confirm", f"Room {roomname} is reserved")
                                conn.sendall(response)
                            
                else:
                    response = responseFormatter("404 Not Found", "Not Found", f"Room {roomname} does not exist")
                    conn.sendall(response)
            elif funcType == "/checkavailability":
                if os.path.exists('rooms.txt'):
                    roomname = name.split("&")[0].strip()
                    endpoints = requestLine.split("?")[1]
                    day = endpoints.split("&")[1].split("=")[1].strip()
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
                        response = responseFormatter("404 Not Found", "Not Found", f"Room {roomname} does not exist")
                        conn.sendall(response)

                    else:
                        if(int(day)>7 or int(day)<0): #invalid input check
                           # print("invalid input for day number /// 400 atilcak")
                            response = responseFormatter("400 Bad Request", "Invalid Input", "Invalid input")
                            conn.sendall(response)
                        else:
                            if os.path.exists('reservations.txt'):
                                roomsFile = open("reservations.txt", "r")
                                for line in roomsFile:    # finds reserved hours
                                    elements = line.split(" ")
                                    if(elements[1] == roomname and elements[3] == day):
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
                                '''
                                conn.sendall("HTTP/1.1 200 OK\n" 
                                             b"Content-Type: text/html\n" 
                                             b"\n" + availableHoursReturn.encode()) 
                                '''
                                print("available hours: ", availableHours)

                                response = responseFormatter("200 OK","Availabiity",f"For room {roomname} available hours at day {day}  are {availableHoursReturn}")
                                conn.sendall(response)

                            ## bu alttaki else ve onun altındaki elif ne işe yarıyor, gereksiz olma ihtimali var      
                            else:
                                response = responseFormatter("200 OK", "title", f"Room {roomname} is available")
                                conn.sendall(response)
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
                    response = responseFormatter("404 Not Found", "title", f"Room {roomname} does not exist")
                    conn.sendall(response)
                else:
                    response = responseFormatter("200 OK", "title", "Room is exist")
                    conn.sendall(response)
            else:
                response = responseFormatter("400 Bad Request", "title", "Invalid input")
                conn.sendall(response)


