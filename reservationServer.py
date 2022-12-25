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

            # url can be like this:
            #/reserve?    room   =    roomname&activity    =    activityname&day    =    x&hour    =    y&duration    =    z:
            #/listavailability?room=roomname&day=x:
            #/listavailability?room=roomname:
            #/display?id=reservation_id:

            reservationId = 0

            funcType= url.split("?")[0] #/display #/reserve
            print("The functype is", funcType)

            name=url.split("?")[1].split("=")[1] # [0] = id , [1] = reservation_id |||| [0] =
            print("The name is", name)
            # -----------------------------------------------------------------------------------------------------
            if(funcType == "/reserve"):
                print("---------------------- reserve forom revervation server -----------------------------")
                if os.path.exists("activities.txt"):

                    roomName = name.split("&")[0]
                    #/reserve  ?   room=roomname    &    activity=activityname    &    day=x    &     hour=y    &    duration=z:
                    endPoints = url.split("?")[1]

                    activityName = endPoints.split("&")[1].split("=")[1]
                    day =  int(endPoints.split("&")[2].split("=")[1])
                    hour =  int(endPoints.split("&")[3].split("=")[1])
                    duration =  int(endPoints.split("&")[4].split("=")[1])
                    isActivityExist = False 

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
                        if response.split(" ")[1].strip() == "200":
                            isActivityExist = True
                        socket2.close()

                    if not isActivityExist:
                        print(f"ERROR {activityName} activity doesn't exist HTTP 404 Not Found message throw")
                        conn.sendall(b"HTTP/1.1 404 Not Found")
                    else:
                        
                        if os.path.exists("rooms.txt"):
                            ##### maybe it is not necessary since we already check whether room exists or not #####                            
                            # with open("rooms.txt", "r") as roomFile:
                            #     for line in roomFile:  # checks whether room exists or not BU LAZIM MI EMİN DEĞİLİM
                            #         if line.strip() == roomName:
                            #             isRoomExist = True
                            #             break
                            # 

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

                            if  responseStatu== "403":
                                
                                print("")                                    
                                conn.sendall(b"HTTP/1.1 403 Forbidden") # room is reserved 
                            else:
                                # bu kısma gerek yok roomServer içinde zaten kontrol ediyor, geçersiz ise hata dönüp buraya girmiyor
                                if (roomName == "" or
                                    day > 7 or
                                    day < 0 or
                                    hour < 9 or
                                    hour + duration - 1 > 17
                                    ):  # invalid input check
                                    print("invalid input day or hour is invalid /// 400 atilcak")
                                else:
                                    """
                                    If all the inputs are valid, then it either reserves the room and sends back an HTTP 200 OK message
                                    it sends back an HTTP 403 Forbidden message indicating that the room is not available.
                                    
                                    If the room is reserved, a reservation_id is generated (which can be 
                                    an integer), and an entry is stored for the reservation_id.
                                    """
                                    # burayı anlamadım ama aşağıda reserve ediyorum id oluşturcam txt'ye yazcam
                                    print("HTTP 200 OK message will be sent, reservation is done with the following informations")
                                    with open("reservationDone.txt", "w") as doneReservations:
                                        doneReservations.write(f"{roomName} is reserved for {activityName} on {day}st/nd/rd/th of the "
                                                               f"week between {hour} - {hour+1} for {duration} hour with the ID {reservationId}")
                                    
                                    with open("reservations.txt", "a+") as reservations:
                                        reservations.write(f"{reservationId} {roomName} {activityName} {day} {hour} {duration}\n")

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






