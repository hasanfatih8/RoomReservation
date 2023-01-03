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
            decodedData = data.decode()
            lines = decodedData.split("\r\n")

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
                            response = responseFormatter("400 Bad Request", "Room Add", f"Room {name} is already exist")              
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

                        response = responseFormatter("404 Not Found", "Room Remove", f"Room {name} does not exist")
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

                        response = responseFormatter("200 OK", "Room Removed", f"Room {name} is removed")             
                        conn.sendall(response)
                else:
                    response = responseFormatter("404 Not Found", "Not Found", f"Room {name} is not exist")
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
                        response = responseFormatter("404 Not Found", "Not Found", f"Room {roomname} does not exist")
                        conn.sendall(response)
                    else:
                        if(roomname == "" or int(day)>7 or int(day)<0 or int(hour)<9 or int(hour)+duration-1>17 or duration<=0): #invalid input check
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

                    print ("1")
                    cacheFlag = False
                    for line in lines:
                        if line.startswith("Cache-Control:"):
                            cache_control = line.split(":", 1)[1].strip()
                            day = line.split("=")[1].split(" ")[0]
                            cacheFlag = True
                            break
                    print ("2")
                    if cacheFlag == False:
                        day = endpoints.split("&")[1].split("=")[1].strip()
                    reservedHours = []
                    controlForRoom = 0
                    rooms = open("rooms.txt", 'r')
                    print ("3")
                    for line in rooms:  # checks whether room exists or not
                        if line.strip() == roomname:
                            controlForRoom = 1
                            break
                    rooms.close()
                    print ("4")
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
                            print ("5")                        
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
                                print ("6")
                                for i in availableHours:
                                    availableHoursReturn += str(i) + " "
                                '''
                                conn.sendall("HTTP/1.1 200 OK\n" 
                                             b"Content-Type: text/html\n" 
                                             b"\n" + availableHoursReturn.encode()) 
                                '''
                                print("available hours: ", availableHours)

                                days = {1: "Monday", 2: "Tuesday", 3: "Wednesday",
                                        4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}

                                if int(day) > 0 and int(day) < 8:
                                     dayName = days[int(day)]
                                else:
                                    dayName = "Invalid day number"
                                print(dayName)

                                print("7")
                                response = responseFormatter(
                                    "200 OK", "Availabiity", f"On {dayName}, Room {roomname} is available for the following hours: {availableHoursReturn}")
                                conn.sendall(response)
                                print("200 OK atildi")
                                print("8")
                            ## bu alttaki else ve onun altındaki elif ne işe yarıyor, gereksiz olma ihtimali var  -- evet gereksiz    
                            else:
                                response = responseFormatter("200 OK", "Availability", f"Room {roomname} is available")
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
                    print("The room name does not exist")
                    response = responseFormatter("404 Not Found", "Not Found", f"Room {roomname} does not exist")
                    conn.sendall(response)
                else:
                    response = responseFormatter("200 OK", "title", "Room is exist")
                    conn.sendall(response)
            else:
                response = responseFormatter("400 Bad Request", "Bad Request", "Invalid input")
                conn.sendall(response)


