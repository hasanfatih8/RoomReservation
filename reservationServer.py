import socket
import os
from splitOperations import *
import time


HOST = "localhost"
PORT = 8080
 
# store the ID in a file
def store_id(id):
    with open('id.txt', 'w') as f:
        f.write(str(id))

# retrieve the ID from a file
def get_id():
    if not os.path.exists('id.txt') or os.stat('id.txt').st_size == 0:
        return 0
    with open('id.txt', 'r') as f:
        id = int(f.read())
    return id

# increase the ID by 1 and store it
def increase_id():
    id = int(get_id())
    id += 1
    store_id(id)

def get_day_name(dayNumber):
    days = {1: "Monday", 2: "Tuesday", 3: "Wednesday",
            4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}

    if int(dayNumber) > 0 and int(dayNumber) < 8:
        dayName = days[int(dayNumber)]
    else:
        dayName = "Invalid day number"
    return dayName


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
            
            reservationId = get_id()

            requestLine,funcType,unnecessary=splitURL(url)
            print("The request line is", requestLine)
            print("The function type is", funcType)

            #name=url.split("?")[1].split("=")[1] # [0] = id , [1] = reservation_id |||| [0] =
            
            #print("The name is", name)
            # -----------------------------------------------------------------------------------------------------
            if(funcType == "/reserve"):
                print("---------------------- reserve from reservation server -----------------------------")
                name=url.split("?")[1].split("=")[1]
                roomName = name.split("&")[0]

                endPoints = url.split("?")[1]

                activityName = endPoints.split("&")[1].split("=")[1]
                day =  int(endPoints.split("&")[2].split("=")[1])
                hour =  int(endPoints.split("&")[3].split("=")[1])
                duration =  int(endPoints.split("&")[4].split("=")[1].split(" ")[0])

                print ("roomName: ", roomName)                                        
                print ("activityName: ", activityName)
                print ("day: ", day)
                print ("hour: ", hour)
                print ("duration: ", duration)
                
                # checks activity 
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfActivityServer:
                    socketOfActivityServer.connect((HOST, 8082))                        
                    socketOfActivityServer.sendall(b"GET /check?name="+ activityName.encode() +
                                                   b" HTTP/1.1")
                    response = socketOfActivityServer.recv(1024).decode("utf-8")
                    print(response.split(" ")[1])
                    socketOfActivityServer.close()                    
                    if response.split(" ")[1].strip() == "404":
                        response = responseFormatter("404 Not Found", "Activity Check", f"404 Not Found")
                        conn.sendall(response)    
                        #conn.sendall(b"HTTP/1.1 404 Not Found\n")
                        print("404 come from activity server")
                    
                    elif response.split(" ")[1].strip() == "200":                                              
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfRoomServer:
                            socketOfRoomServer.connect((HOST, 8081))                                  
                            socketOfRoomServer.sendall(b"GET /reserve?room="+roomName.encode() +
                                                       b"&day=" + str(day).encode() +
                                                       b"&hour=" + str(hour).encode() +
                                                       b"&duration=" + str(duration).encode() + 
                                                       b" HTTP/1.1")

                            response = socketOfRoomServer.recv(1024).decode("utf-8")
                            print("Received from room server: ", response)    
                            print("Received from room server: ", response)    
                            print("Received from room server: ", response)    
                            print("Received from room server: ", response)    
                            print("Received from room server: ", response)    
                            responseStatus=  response.split(" ")[1].strip()                                
                            socketOfRoomServer.close()

                        if  responseStatus== "403":   
                            response = responseFormatter("403 Forbidden", "Already reserved", f"Room {roomName} is already reserved")                #maybe except 200 are unnecessary                                         
                            conn.sendall(response) 
                            print("403 from room") 
                        elif responseStatus == "404":
                            response = responseFormatter("404 Not Found", "Not Found", f"Room {roomName} does not exist")
                            conn.sendall(response)
                        elif responseStatus == "400":
                            response = responseFormatter("400 Bad Request", "Invalid Input", "Invalid input")
                            conn.sendall(response) 
                            print("400 from room")
                        elif responseStatus == "200":
                                with open("reservations.txt", "a+") as reservations:
                                    reservations.write(f"{reservationId} {roomName} {activityName} {day} {hour} ")
                                    for i in range(1,duration):
                                        hours = int(hour) + i                 
                                        reservations.write(str(hours) + " ")                                       
                                    reservations.write("\n")

                                increase_id()
                                response = responseFormatter("200 OK", "Reservation Succesful", f"Room {roomName} is reserved for activity {activityName} on {get_day_name(day)}   at {hour}:00 -  {hour+duration}:00 hours. Your Reservation ID: {reservationId}")
                                conn.sendall(response)
                                #conn.sendall(b"HTTP/1.1 200 OK")
            
            #elif funcType == "/listavailability": #/listavailability?room=roomname&day=x:
            #    print("------ listavailability -------")
            #    
            #    #name = name.split("?")[1].split("&")[0]
            #    #day = int(url.split("=")[1])
            #    
            #    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfRoomServer:
            #        socketOfRoomServer.connect((HOST, 8081))                                    
            #
            #        socketOfRoomServer.sendall(b"/get?room=emine")
            #        response = socketOfRoomServer.recv(1024).decode("utf-8")
            #        print("Received from room server: ", response)   
            #
            #        socketOfRoomServer.close()
            
            elif funcType == "/listavailability":    #/listavailability?room=roomname  
                                                     #/listavailability?room=roomname&day=x:             
                print ("------ listavailability -------")
                endPoints = url.split("?")[1]
                # if we want to get information about a specific day
                if(endPoints.__contains__("&")):
                    roomName = endPoints.split("&")[0].split("=")[1]
                    day = int(endPoints.split("&")[1].split("=")[1].split(" ")[0])
                    print ("roomName: ", roomName)
                    print ("day: ", day)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfRoomServer:
                        socketOfRoomServer.connect((HOST, 8081))                        
                        socketOfRoomServer.sendall(b"GET /checkavailability?room="+roomName.encode() + 
                                                   b"&day=" + str(day).encode() + 
                                                   b" HTTP/1.1")
                        response = socketOfRoomServer.recv(1024).decode("utf-8")
                        print("Received from room server: ", response)    
                        responseStatus =  response.split(" ")[1].strip()                                
                        
                        bodyText = response.split("\n")[4].split("<body>")[1].split("</body>")[0]

                        if  responseStatus== "403":                   #maybe except 200 are unnecessary                                         
                            
                            print("403 from room")
                            response = responseFormatter("403 Forbidden", "Room Check", f"403 Forbidden")                            

                        elif responseStatus == "404":
                            print("404 from room")
                            response = responseFormatter("404 Not Found", "Room Check", f"404 Not Found")   
                            
                        elif responseStatus == "400":                        
                            print("400 from room")
                            response = responseFormatter("400 Bad Request", "Room Check", f"400 Bad Request")
                            
                        elif responseStatus == "200":
                            response = responseFormatter("200 OK", "Available Hours", bodyText)
                            
                        else:
                            response = responseFormatter("400 Bad Request", "Room Check", f"400 Bad Request")
                            
                        conn.sendall(response)
                        socketOfRoomServer.close()
                else:
                    
                    roomName = endPoints.split(" ")[0].split("=")[1]
                    print ("roomName: ", roomName)
                    bodyText=""   
                    for day in range(1, 8):
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfRoomServer:
                                socketOfRoomServer.connect((HOST, 8081))                                                                                                                         
                                socketOfRoomServer.sendall(b"GET /checkavailability?room="+roomName.encode() + 
                                                        b"&day=" + str(day).encode() +
                                                        b" HTTP/1.1")  
                                                                                          
                                responseText = socketOfRoomServer.recv(1024).decode("utf-8")
                                print("Received from room server: ", responseText)    
                                responseStatus = responseText.split(" ")[1].strip()
                                print("responseStatus: ", responseStatus)
                                                   
                               
                                
                                if  responseStatus== "403":
                                    response = responseFormatter("403 Forbidden", "Room Check", f"403 Forbidden")
                                    break

                                elif responseStatus == "404":
                                    response = responseFormatter("404 Not Found", "Room Check", f"404 Not Found")
                                    break
                                    
                                elif responseStatus == "400":
                                    response = responseFormatter("400 Bad Request", "Room Check", f"400 Bad Request")
                                    break
                                    
                                elif responseStatus == "200":
                                    print("200 from room for day: ", day)
                                    bodyText += responseText.split("\n")[4].split("<body>")[1].split("</body>")[0].strip() + "<br>"
                                    if day == 7:
                                        print("bodyText: ", bodyText)                                         
                                        response = responseFormatter("200 OK", "Available Hours", f"{bodyText}")                                                                                                                        
                                        conn.sendall(response)
                                        break    
                                                                                                          
                                else:
                                    response = responseFormatter("400 Bad Request", "Room Check", f"400 Bad Request") 
                                    break                                   

                                socketOfRoomServer.close()
                    
                    print("bodyText: ", bodyText)      
                                                                                                  
                    # give hello world response
                    conn.sendall(response)


                            
                            


            elif funcType == "/display": #/display?id=reservation_id:
                print("------ display -------")
                endPoints = url.split("?")[1]
                name=url.split("?")[1].split("=")[1]
                id = name.split(" ")[0]
                print("id: ", id)
                with open("reservations.txt", "r") as reservations:
                    for line in reservations:
                        if line.split(" ")[0] == id:
                            arr = line.split(" ")
                            duration = 1
                            if(arr[5] == "\n"):
                                duration = 1
                            else:
                                duration = int(arr[-2])-int(arr[4])
                            print(arr)
                            response = responseFormatter("200 OK", "Display", f"Reservation ID: {id}, Room: {line.split(' ')[1]}, Activity: {line.split(' ')[2]}, When: {get_day_name(line.split(' ')[3])}   {line.split(' ')[4]}:00 - {str(int(arr[4])+duration+1)}:00")
                            conn.sendall(response)
                            """
                            conn.sendall(b"HTTP/1.1 200 OK\n"+
                                         b"&id=" + line.split(" ")[0].encode()+
                                         b"&roomname=" + line.split(" ")[1].encode()+
                                         b"&activityname=" + line.split(" ")[2].encode()+
                                         b"&day=" + line.split(" ")[3].encode()+
                                         b"&hour=" + line.split(" ")[4].encode()+
                                         b"&until=" + line.split(" ")[-1].encode())
                            """
                            # 1 emine act1 6 13 14 15 16 
                            print("200 from display")
                            break
                    else:
                        response = responseFormatter("404 Not Found", "Display", f"Reservation ID {id} does not exist.")
                        conn.sendall(response)
                        print("404 from display")
            elif(funcType == "/favicon.ico"):
                pass
            else:
                response = responseFormatter("400 Bad Request", "Welcome", "Welcome to our reservation server, please type proper commands in the URL bar.")
                conn.sendall(response)


# hasan branch





