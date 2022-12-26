import socket
import os

HOST = "localhost"
PORT = 8080

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
            
            reservationId = 0

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
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket2:
                    socket2.connect((HOST, 8082))                        
                    socket2.sendall(b"/check?name="+ activityName.encode())
                    response = socket2.recv(1024).decode("utf-8")
                    print(response.split(" ")[1])
                    socket2.close()                    
                    if response.split(" ")[1].strip() == "404":
                        conn.sendall(b"HTTP/1.1 404 Not Found\n")
                        print("404 come from activity server")
                    
                    elif response.split(" ")[1].strip() == "200":                                              
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket1:
                            socket1.connect((HOST, 8081))                                  
                            socket1.sendall(b"/reserve?room="+roomName.encode() +
                                            b"&day=" + str(day).encode() +
                                            b"&hour=" + str(hour).encode() +
                                            b"&duration=" + str(duration).encode())

                            response = socket1.recv(1024).decode("utf-8")
                            print("Received from room server: ", response)    
                            responseStatu=  response.split(" ")[1].strip()                                
                            socket1.close()

                        if  responseStatu== "403":                   #maybe except 200 are unnecessary                                         
                            conn.sendall(b"HTTP/1.1 403 Forbidden\n") 
                            print("403 from room") 
                        elif responseStatu == "404":
                            conn.sendall(b"HTTP/1.1 404 Not Found\n")
                            print("404 from room")
                        elif responseStatu == "400":
                            conn.sendall(b"HTTP/1.1 400 Bad Request\n") 
                            print("400 from room")
                        elif responseStatu == "200":
                                with open("reservations.txt", "a+") as reservations:
                                    reservations.write(f"{reservationId} {roomName} {activityName} {day} {hour} ")
                                    for i in range(1,duration):
                                        hours = int(hour) + i                 
                                        reservations.write(str(hours) + " ")                                       
                                    reservations.write("\n")

                                reservationId += 1

                                conn.sendall(b"HTTP/1.1 200 OK")
            
            elif funcType == "/listavailability": #/listavailability?room=roomname&day=x:
                print("------ listavailability -------")
                
                #name = name.split("?")[1].split("&")[0]
                #day = int(url.split("=")[1])
                
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket1:
                    socket1.connect((HOST, 8081))                                    

                    socket1.sendall(b"/get?room=emine")
                    response = socket1.recv(1024).decode("utf-8")
                    print("Received from room server: ", response)   

                    socket1.close()

            elif funcType == "/listavailability":    #/listavailability?room=roomname               
                print ("------ listavailability -------")
            elif funcType == "/display": #/display?id=reservation_id:
                print("------ display -------")
            else:
                s.sendall(b"HTTP 400 Bad Request")


# hasan branch

#def contactRoomServer(day):
#    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket1:
#        socket1.connect((HOST, 8081))                                    
#
#        socket1.sendall(b"/get?room=emine")
#        response = socket1.recv(1024).decode("utf-8")
#        print("Received from room server: ", response)    
#        # check the response 
#
#        socket1.close()






