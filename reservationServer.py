import socket
import os
from splitOperations import *

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
            
            reservationId = get_id()

            funcType= url.split("?")[0] #/display #/reserve
            print("The functype is", funcType)

            name=url.split("?")[1].split("=")[1] # [0] = id , [1] = reservation_id |||| [0] =
            print("The name is", name)
            # -----------------------------------------------------------------------------------------------------
            if(funcType == "/reserve"):
                print("---------------------- reserve from reservation server -----------------------------")
                roomName = name.split("&")[0]

                endPoints = url.split("?")[1]

                activityName = endPoints.split("&")[1].split("=")[1]
                day =  int(endPoints.split("&")[2].split("=")[1])
                hour =  int(endPoints.split("&")[3].split("=")[1])
                duration =  int(endPoints.split("&")[4].split("=")[1])

                print ("roomName: ", roomName)                                        
                print ("activityName: ", activityName)
                print ("day: ", day)
                print ("hour: ", hour)
                print ("duration: ", duration)
                
                # checks activity 
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfActivityServer:
                    socketOfActivityServer.connect((HOST, 8082))                        
                    socketOfActivityServer.sendall(b"/check?name="+ activityName.encode())
                    response = socketOfActivityServer.recv(1024).decode("utf-8")
                    print(response.split(" ")[1])
                    socketOfActivityServer.close()                    
                    if response.split(" ")[1].strip() == "404":
                        conn.sendall(b"HTTP/1.1 404 Not Found\n")
                        print("404 come from activity server")
                    
                    elif response.split(" ")[1].strip() == "200":                                              
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfRoomServer:
                            socketOfRoomServer.connect((HOST, 8081))                                  
                            socketOfRoomServer.sendall(b"/reserve?room="+roomName.encode() +
                                            b"&day=" + str(day).encode() +
                                            b"&hour=" + str(hour).encode() +
                                            b"&duration=" + str(duration).encode())

                            response = socketOfRoomServer.recv(1024).decode("utf-8")
                            print("Received from room server: ", response)    
                            responseStatus=  response.split(" ")[1].strip()                                
                            socketOfRoomServer.close()

                        if  responseStatus== "403":                   #maybe except 200 are unnecessary                                         
                            conn.sendall(b"HTTP/1.1 403 Forbidden\n") 
                            print("403 from room") 
                        elif responseStatus == "404":
                            conn.sendall(b"HTTP/1.1 404 Not Found\n")
                            print("404 from room")
                        elif responseStatus == "400":
                            conn.sendall(b"HTTP/1.1 400 Bad Request\n") 
                            print("400 from room")
                        elif responseStatus == "200":
                                with open("reservations.txt", "a+") as reservations:
                                    reservations.write(f"{reservationId} {roomName} {activityName} {day} {hour} ")
                                    for i in range(1,duration):
                                        hours = int(hour) + i                 
                                        reservations.write(str(hours) + " ")                                       
                                    reservations.write("\n")

                                increase_id()

                                conn.sendall(b"HTTP/1.1 200 OK")
            
            elif funcType == "/listavailability": #/listavailability?room=roomname&day=x:
                print("------ listavailability -------")
                
                #name = name.split("?")[1].split("&")[0]
                #day = int(url.split("=")[1])
                
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfRoomServer:
                    socketOfRoomServer.connect((HOST, 8081))                                    

                    socketOfRoomServer.sendall(b"/get?room=emine")
                    response = socketOfRoomServer.recv(1024).decode("utf-8")
                    print("Received from room server: ", response)   

                    socketOfRoomServer.close()

            elif funcType == "/listavailability":    #/listavailability?room=roomname               
                print ("------ listavailability -------")
                endPoints = url.split("?")[1]
                if(endPoints.__contains__("&")):
                    roomName = endPoints.split("&")[0].split("=")[1]
                    day = int(endPoints.split("&")[1].split("=")[1])
                    print ("roomName: ", roomName)
                    print ("day: ", day)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfRoomServer:
                        socketOfRoomServer.connect((HOST, 8081))                        
                        socketOfRoomServer.sendall(b"/get?room="+roomName.encode() + 
                                                   b"&day=" + str(day).encode())
                        response = socketOfRoomServer.recv(1024).decode("utf-8")
                        print("Received from room server: ", response)    
                        responseStatus=  response.split(" ")[1].strip()                                
                        socketOfRoomServer.close()

                        if  responseStatus== "403":                   #maybe except 200 are unnecessary                                         
                            conn.sendall(b"HTTP/1.1 403 Forbidden\n") 
                            print("403 from room") 
                        elif responseStatus == "404":
                            conn.sendall(b"HTTP/1.1 404 Not Found\n")
                            print("404 from room")
                        elif responseStatus == "400":
                            conn.sendall(b"HTTP/1.1 400 Bad Request\n") 
                            print("400 from room")
                        elif responseStatus == "200":
                            conn.sendall(b"HTTP/1.1 200 OK\n" + response.encode())
                else:
                    roomName = endPoints.split("=")[1]
                    print ("roomName: ", roomName)
                    for day in range(1,8):
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfRoomServer:
                            socketOfRoomServer.connect((HOST, 8081))                        
                            socketOfRoomServer.sendall(b"/get?room="+roomName.encode()+
                                                       b"&day=" + str(day).encode())
                            response = socketOfRoomServer.recv(1024).decode("utf-8")
                            print("Received from room server: ", response)    
                            responseStatus=  response.split(" ")[1].strip()                                
                            socketOfRoomServer.close()

                            if  responseStatus== "403":
                                conn.sendall(b"HTTP/1.1 403 Forbidden\n") 
                                print("403 from room") 
                            elif responseStatus == "404":
                                conn.sendall(b"HTTP/1.1 404 Not Found\n")
                                print("404 from room")
                            elif responseStatus == "400":
                                conn.sendall(b"HTTP/1.1 400 Bad Request\n") 
                                print("400 from room")
                            elif responseStatus == "200":
                                conn.sendall(b"HTTP/1.1 200 OK\n" + response.encode())

            elif funcType == "/display": #/display?id=reservation_id:
                print("------ display -------")
                endPoints = url.split("?")[1]
                id = endPoints.split("=")[1]
                print("id: ", id)
                with open("reservations.txt", "r") as reservations:
                    for line in reservations:
                        if line.split(" ")[0] == id:
                            conn.sendall(b"HTTP/1.1 200 OK\n"+
                                         b"&id=" + line.split(" ")[0].encode()+
                                         b"&roomname=" + line.split(" ")[1].encode()+
                                         b"&activityname=" + line.split(" ")[2].encode()+
                                         b"&day=" + line.split(" ")[3].encode()+
                                         b"&hour=" + line.split(" ")[4].encode()+
                                         b"&until=" + line.split(" ")[-1].encode())
                            # 1 emine act1 6 13 14 15 16 
                            print("200 from display")
                            break
                    else:
                        conn.sendall(b"HTTP/1.1 404 Not Found\n")
                        print("404 from display")
            else:
                response = responseFormatter("400 Bad Request", "Welcome", "Welcome to our reservation server, please type proper commands in the URL bar.")
                conn.sendall(response)


# hasan branch





