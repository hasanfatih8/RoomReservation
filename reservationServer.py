import socket
import os
from splitOperations import *

# Indicate the host and the port number
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

# With command, we don't need to use try catch blocks
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    # bind the socket to the host and port
    s.bind((HOST, PORT))
    s.listen() # if you put any number in this function ex: 5, it means that it will listen 5 connections after that it is going to throw an error
    while True:
        # Connection object will be stored in conn, list of ip addresses will be storedin addr
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
            
            # For reservations, we need to get the reservation ID
            reservationId = get_id()
            
            # split the url to get the function type and the name
            requestLine,funcType,unnecessary=splitURL(url)
            print("The request line is", requestLine)
            print("The function type is", funcType)

            name=url.split("?")[1].split("=")[1] # [0] = id , [1] = reservation_id |||| [0] =
            
            print("The name is", name)

            # Do reservation
            if(funcType == "/reserve"):
                print("---------------------- reserve from reservation server -----------------------------")

                # get the room name, activity name, dayinfo, hourinfo, duration
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
                
                # Create a socket to connect to the activity server
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfActivityServer:
                    # Connect to the activity server
                    socketOfActivityServer.connect((HOST, 8082))   
                    # Send the request to the activity server                     
                    socketOfActivityServer.sendall(b"GET /check?name="+ activityName.encode() +
                                                   b" HTTP/1.1")
                    # Receive the response from the activity server
                    response = socketOfActivityServer.recv(1024).decode("utf-8")
                    print(response.split(" ")[1])
                    socketOfActivityServer.close()       
                    # Check the response status, if it is 404, send 404 to the client(reservation server)             
                    if response.split(" ")[1].strip() == "404":
                        response = responseFormatter("404 Not Found", "Activity Check", f"404 Not Found")
                        conn.sendall(response)    
                        #conn.sendall(b"HTTP/1.1 404 Not Found\n")
                        print("404 come from activity server")
                    # If the response status is 200, send the request to the room server
                    elif response.split(" ")[1].strip() == "200":                
                        # Create a socket to connect to the room server                              
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfRoomServer:
                            # Connect to the room server
                            socketOfRoomServer.connect((HOST, 8081))              
                            # Send the request to the room server                    
                            socketOfRoomServer.sendall(b"GET /reserve?room="+roomName.encode() +
                                                       b"&day=" + str(day).encode() +
                                                       b"&hour=" + str(hour).encode() +
                                                       b"&duration=" + str(duration).encode() + 
                                                       b" HTTP/1.1")
                            # Receive the response from the room server
                            response = socketOfRoomServer.recv(1024).decode("utf-8")
                            print("Received from room server: ", response)    
                            print("Received from room server: ", response)    
                            print("Received from room server: ", response)    
                            print("Received from room server: ", response)    
                            print("Received from room server: ", response)    
                            # Send the response to the client(reservation server)
                            responseStatus=  response.split(" ")[1].strip()                                
                            socketOfRoomServer.close()
                        # Check the response status, and send different responses according to the client(reservation server)
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
                                # Write the reservation to the file
                                with open("reservations.txt", "a+") as reservations:
                                    reservations.write(f"{reservationId} {roomName} {activityName} {day} {hour} ")
                                    for i in range(1,duration):
                                        hours = int(hour) + i                 
                                        reservations.write(str(hours) + " ")                                       
                                    reservations.write("\n")
                                
                                increase_id()
                                # Send the response to the client(reservation server)
                                response = responseFormatter("200 OK", "Reservation Succesful", f"Room {roomName} is reserved for activity {activityName} on day {day} at {hour} for {duration} hours. \n your Reservation ID: {reservationId}")
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

            # List the availability of a room
            elif funcType == "/listavailability":    #/listavailability?room=roomname  
                                                     #/listavailability?room=roomname&day=x:             
                print ("------ listavailability -------")
                endPoints = url.split("?")[1]
                # If we want to get information about a specific day
                if(endPoints.__contains__("&")):
                    # Get the room name and the day
                    roomName = endPoints.split("&")[0].split("=")[1]
                    day = int(endPoints.split("&")[1].split("=")[1].split(" ")[0])
                    print ("roomName: ", roomName)
                    print ("day: ", day)
                    # Create a socket to connect to the room server
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfRoomServer:
                        # Connect to the room server
                        socketOfRoomServer.connect((HOST, 8081))               
                        # Send the request to the room server         
                        socketOfRoomServer.sendall(b"GET /checkavailability?room="+roomName.encode() + 
                                                   b"&day=" + str(day).encode() + 
                                                   b" HTTP/1.1")
                        # Receive the response from the room server
                        response = socketOfRoomServer.recv(1024).decode("utf-8")
                        print("Received from room server: ", response)    
                        # Format the response
                        responseStatus =  response.split(" ")[1].strip()                                
                        socketOfRoomServer.close()
                        # Check the response status, and send different responses according to the client(reservation server)
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

                # If we want to get information about all days
                else:
                    # Get the room name
                    roomName = endPoints.split("=")[1]
                    print ("roomName: ", roomName)
                    # Do the same thing for all days
                    for day in range(1,8):
                        # Create a socket to connect to the room server
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketOfRoomServer:
                            # Connect to the room server
                            socketOfRoomServer.connect((HOST, 8081))      
                            # Send the request to the room server
                            socketOfRoomServer.sendall(b"GET /checkavailability?room="+roomName.encode() + 
                                                       b"&day=" + str(day).encode() +
                                                       b" HTTP/1.1")
                            """
                            # Build the query string
                            query_string = "room=" + roomName + "&day=" + str(day)
                            # Build the GET request
                            request = "GET /checkavailability?" + query_string + " HTTP/1.1\r\n"
                            # Send the request
                            socketOfRoomServer.sendall(request.encode())
                            """  
                            # Receive the response from the room server
                            response = socketOfRoomServer.recv(1024).decode("utf-8")
                            print("Received from room server: ", response)   
                            # Format the response 
                            responseStatus=  response.split(" ")[1].strip()                                
                            socketOfRoomServer.close()
                            # Check the response status, and send different responses according to the client(reservation server)
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
            # Discplay a reservation according to it's reservation id
            elif funcType == "/display": #/display?id=reservation_id:
                print("------ display -------")
                # Get the reservation id
                endPoints = url.split("?")[1]
                id = name.split(" ")[0]
                print("id: ", id)
                # Open the reservations file
                with open("reservations.txt", "r") as reservations:
                    for line in reservations:
                        # Find the reservation with the given id
                        if line.split(" ")[0] == id:
                            arr = line.split(" ")
                            duration = 1
                            # Calculate the duration of the reservation
                            if(arr[5] == "\n"):
                                duration = 1
                            else:
                                duration = int(arr[-2])-int(arr[4])
                            print(arr)
                            # Send the response to the client
                            response = responseFormatter("200 OK", "Display", f"Reservation ID: {id}, Room: {line.split(' ')[1]}, Activity: {line.split(' ')[2]}, When: day{line.split(' ')[3]} {line.split(' ')[4]}:00 - {str(int(arr[4])+duration)}:00")
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
                        # If the reservation id does not exist, send 404 response
                        response = responseFormatter("404 Not Found", "Display", f"Reservation ID {id} does not exist.")
                        conn.sendall(response)
                        print("404 from display")
            # For all bad requests
            else:
                response = responseFormatter("400 Bad Request", "Welcome", "Welcome to our reservation server, please type proper commands in the URL bar.")
                conn.sendall(response)
