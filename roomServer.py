import socket
import os.path

from splitOperations import *

# Inditcate localhost and port number
HOST = "localhost"
PORT = 8081

# With command, we don't need to use try catch blocks
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
    # bind the socket to the host and port
    s.bind((HOST, PORT)) 
    s.listen() # if you put any number in this function ex: 5, it means that it will listen 5 connections after that it is going to throw an error
    while True:
        # Connection object will be stored in conn, list of ip addresses will be storedin addr 
        conn, addr = s.accept() 

        with conn:
            print(f"Connected by {addr}")

            # take the first 1024 byte, other than that can be junk
            data = conn.recv(1024) 

            # For cache control, decode another data and split it
            decodedData = data.decode()
            lines = decodedData.split("\r\n")

            # Check if the data is empty
            if not data:
                break
            # Check if the request is for the favicon
            if b"favicon.ico" in data:
            # Ignore the request and do not send a response
                pass
            url= data.decode("utf-8")
            print("The url is", url)
            
            # Split the url and get the request line, function type and name
            requestLine,funcType,name=splitURL(url)           

            # Add the room to server
            if funcType == "/add":
                isExists = 0
                if os.path.exists('rooms.txt'):
                    lines = []
                    file = open("rooms.txt", 'r')                      
                    for line in file:
                        # If the room is already exist, send 400 error
                        if(name == line.strip()):                                                        
                            response = responseFormatter("400 Bad Request", "Room Add", f"Room {name} is already exist")              
                            conn.sendall(response)
                            isExists = 1
                            file.close()
                            break
                # If the room is not exist, add the room to server and return 200 OK
                if(isExists == 0):
                    file = open("rooms.txt", 'a')                   
                    file.write(name)
                    file.write("\n")

                    response = responseFormatter("200 OK", "Room Added", f"Room {name} is added")    
                    conn.sendall(response)

                    file.close()
                    
            # Remove the room from server        
            elif funcType == "/remove":
                # Read the file and check if the room is exist
                if os.path.exists('rooms.txt'):
                    lines = []
                    file = open("rooms.txt", 'r')
                    for line in file:
                        lines.append(line.strip())
                    file.close()
                    for line in lines:
                        print(line)
                    # If the room is not exist, send 404 error
                    if not lines.__contains__(name):

                        response = responseFormatter("404 Not Found", "Room Remove", f"Room {name} does not exist")
                        conn.sendall(response)
                    # If the room is exist, remove the room from server and return 200 OK
                    else:
                        print("The room name is  exist")                                        
                        file = open("rooms.txt", 'w')
                        file.seek(0)
                        lines.remove(name)
                        for line in lines:                                                     
                            file.write(line)
                            file.write("\n")
                        file.close()

                        response = responseFormatter("200 OK", "Room Removed", f"Room {name} is removed")             
                        conn.sendall(response)
                # If the file is not exist, send 404 error        
                else:
                    response = responseFormatter("404 Not Found", "Not Found", f"Room {name} is not exist")
                    conn.sendall(response)
            # Reserve the room for the given time        
            elif funcType == "/reserve":
                if os.path.exists('rooms.txt'):  
                    # Split the request line to get the room name, day, hour and duration
                    roomname = name.split("&")[0].strip()
                    endpoints = requestLine.split("?")[1]
                    day = endpoints.split("&")[1].split("=")[1].strip()
                    hour = endpoints.split("&")[2].split("=")[1].strip ()
                    duration = int(endpoints.split("&")[3].split("=")[1].strip())

                    print("roomname",roomname,"day",day,"hour",hour,"duration",duration)
                    # Check if the room is exist
                    controlForRoom = 0
                    rooms = open("rooms.txt", 'r')    
                    for line in rooms:  # checks whether room exists or not BU LAZIM MI EMİN DEĞİLİM
                        print("line",line,"roomname",roomname)
                        if line.strip() == roomname:
                            controlForRoom = 1
                            break
                    rooms.close()

                    print("controlForRoom",controlForRoom)
                    # If the room does not exist, send 404 error
                    if(controlForRoom == 0):   
                        response = responseFormatter("404 Not Found", "Not Found", f"Room {roomname} does not exist")
                        conn.sendall(response)
                    # If the room exists, check if the room is already reserved for the given time
                    else:
                        # Check if the input is valid
                        if(roomname == "" or int(day)>7 or int(day)<0 or int(hour)<9 or int(hour)+duration-1>17): #invalid input check
                            print("invalid input 400 atilcak")
                            
                            response = responseFormatter("400 Bad Request", "Invalid Input", "Invalid input")
                            conn.sendall(response)
                        # If the input is valid, check if the room is already reserved for the given time
                        else:
                            isReserved = 0 #if room already reserved sets to 1
                            if os.path.exists('reservations.txt'):
                                print("reservations.txt exists")
                                reservationFileRead = open("reservations.txt", "r")

                                # Check if the room is already reserved for the given time
                                for line in reservationFileRead:
                                    print("line",line)
                                    elements = line.split(" ")
                                    # 
                                    if(elements[1] == roomname and elements[3] == day):
                                        hoursLength = len(elements) - 4                       

                                        # If starting hour of new reservation matches with other reservation
                                        for i in range(0,hoursLength):                                                    
                                            if(elements[i + 4].strip() == hour):
                                                isReserved = 1     
                                                break
                                        # If starting hour of new reservation is between other reservation
                                        for j in range(0,hoursLength):                                                                             
                                            if(elements[j + 4].strip() == str(int(hour) + duration - 1)):
                                                isReserved = 1     
                                                break
                                    if(isReserved == 1):                                                                                
                                        break
                                reservationFileRead.close()

                            print("isReserved",isReserved)
                            # If the room is already reserved for the given time, send 403 error
                            if(isReserved == 1):
                                print("already reserved 403 atilcak")
                                response = responseFormatter("403 Forbidden", "Already reserved", f"Room {roomname} is already reserved")
                                conn.sendall(response)

                            # If the room is not reserved for the given time, reserve the room for the given time
                            else:
                                print("reserved 200 atilcak")
                                response = responseFormatter("200 OK", "Reservation Confirm", f"Room {roomname} is reserved")
                                conn.sendall(response)
                # If room does not exist, send 404 error         
                else:
                    response = responseFormatter("404 Not Found", "Not Found", f"Room {roomname} does not exist")
                    conn.sendall(response)
            # Check availability for the given room
            elif funcType == "/checkavailability":
                if os.path.exists('rooms.txt'):
                    roomname = name.split("&")[0].strip()
                    endpoints = requestLine.split("?")[1]
                    # Check if reservation server is sending consecutive requests, if yes,
                    # Then it means reservation server wants to check availability for specified day. 
                    cacheFlag = False
                    for line in lines:
                        if line.startswith("Cache-Control:"):
                            cache_control = line.split(":", 1)[1].strip()
                            day = line.split("=")[1].split(" ")[0]
                            cacheFlag = True
                            break
                    # Check availability for specified day
                    if cacheFlag == False:
                        day = endpoints.split("&")[1].split("=")[1].strip()
                    # Track the reserved hours in a list
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
                        # If room does not exist, send 404 error
                        response = responseFormatter("404 Not Found", "Not Found", f"Room {roomname} does not exist")
                        conn.sendall(response)
                    # If room exists, check if the room is already reserved for the given time
                    else:
                        # Check if the input is valid
                        if(int(day)>7 or int(day)<0): 
                           # print("invalid input for day number /// 400 atilcak")
                            response = responseFormatter("400 Bad Request", "Invalid Input", "Invalid input")
                            conn.sendall(response)
                        else:
                            # Check if the room is already reserved for the given time
                            if os.path.exists('reservations.txt'):
                                roomsFile = open("reservations.txt", "r")
                                for line in roomsFile:    # finds reserved hours
                                    elements = line.split(" ")
                                    if(elements[1] == roomname and elements[3] == day):
                                        hoursLength = len(elements) - 2
                                        for i in range(0,hoursLength):
                                            reservedHours.append(elements[i + 2].strip())
                                roomsFile.close()
                                # Find available hours
                                availableHours = []
                                availableHoursReturn = ""
                                for i in range(0,9):    # finds available hours
                                    # If the hour is not reserved, add it to the available hours list
                                    if(str(i+9) not in reservedHours):
                                        availableHours.append(i+9)
                                # Format the available hours list
                                for i in availableHours:
                                    availableHoursReturn += str(i) + " "
                                '''
                                conn.sendall("HTTP/1.1 200 OK\n" 
                                             b"Content-Type: text/html\n" 
                                             b"\n" + availableHoursReturn.encode()) 
                                '''
                                print("available hours: ", availableHours)
                                # Send the available hours to the reservation server
                                response = responseFormatter("200 OK","Availabiity",f"For room {roomname} available hours at day {day}  are {availableHoursReturn}")
                                conn.sendall(response)

                            ## bu alttaki else ve onun altındaki elif ne işe yarıyor, gereksiz olma ihtimali var      
                            else:
                                response = responseFormatter("200 OK", "Availability", f"Room {roomname} is available")
                                conn.sendall(response)
            elif funcType == "/get": #listavailability?room=roomname
                
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
                    print("The room name does not exist")
                    response = responseFormatter("404 Not Found", "Not Found", f"Room {roomname} does not exist")
                    conn.sendall(response)
                else:
                    response = responseFormatter("200 OK", "title", "Room is exist")
                    conn.sendall(response)
            else:
                response = responseFormatter("400 Bad Request", "Bad Request", "Invalid input")
                conn.sendall(response)


