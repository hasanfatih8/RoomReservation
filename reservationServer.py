import socket
import os
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
            #/reserve?    room   =    roomname&activity    =    activityname&day    =    x&hour    =    y&duration    =    z:
            #/listavailability?room=roomname&day=x:
            #/listavailability?room=roomname:
            #/display?id=reservation_id:
            reservationId = 0
            funcType= url.split("?")[0] #/display #/reserve
            print("The functype is", funcType)

            name=url.split("?")[1].split("=")[1] # [0] = id , [1] = reservation_id |||| [0] =
            print("The name is", name)

            if(funcType == "/reserve"):
                if os.path.exists("activities.txt"):
                    roomName = name.split("&")[0]
                    #/reserve  ?   room=roomname    &    activity=activityname    &    day=x    &     hour=y    &    duration=z:
                    endPoints = url.split("?")[1]
                    activityName = endPoints.split("&")[1].split("=")[1]
                    day =  int(endPoints.split("&")[2].split("=")[1])
                    hour =  int(endPoints.split("&")[3].split("=")[1])
                    duration =  int(endPoints.split("&")[4].split("=")[1])
                    isActivityExist = False
                    with open("activities.txt", "r") as activityFile:
                        for line in activityFile:  # checks whether room exists or not BU LAZIM MI EMİN DEĞİLİM
                            if line.strip() == activityName:
                                isActivityExist = True
                                break
                    if not isActivityExist:
                        print(f"ERROR {activityName} activity doesn't exist HTTP 404 Not Found message throw")
                    else:
                        if os.path.exists("rooms.txt"):
                            ##### maybe it is not necessary since we already check whether room exists or not #####
                            isRoomExist = False
                            with open("rooms.txt", "r") as roomFile:
                                for line in roomFile:  # checks whether room exists or not BU LAZIM MI EMİN DEĞİLİM
                                    if line.strip() == roomName:
                                        isRoomExist = True
                                        break
                            if not isRoomExist:
                                print(f"ERROR {roomName} room doesn't exist HTTP NE MESAJI YOLLUCAZ PDFTE SÖYLEMİYO 404 Not Found message throw")
                            else:
                                if (roomName == "" or
                                    day > 7 or
                                    day < 0 or
                                    hour < 9 or
                                    hour + duration - 1 > 17
                                    ):  # invalid input check
                                    print("invalid input day or hour is invalid /// 400 atilcak")
                                else:
                                    """
                                    If all the inputs are valid, then it either reserves the room and sends 
                                    back an HTTP 200 OK message, or it sends back an HTTP 403 Forbidden message indicating 
                                    that the room is not available. If the room is reserved, a reservation_id is generated (which can be 
                                    an integer), and an entry is stored for the reservation_id.
                                    """
                                    # burayı anlamadım ama aşağıda reserve ediyorum id oluşturcam txt'ye yazcam
                                    print("HTTP 200 OK message will be sent, reservation is done with the following informations")
                                    with open("reservationDone.txt", "w") as doneReservations:
                                        doneReservations.write(f"{roomName} is reserved for {activityName} on {day}st/nd/rd/th of the "
                                                               f"week between {hour} - {hour+1} for {duration} hour with the ID {reservationId}")
                                        reservationId += 1
            elif funcType == "/listavailability":
                #/listavailability     ?      room=roomname    &     day=x:

                roomName = name.split("&")[0]
                endPoints = url.split("?")[1]
                day = int(endPoints.split("&")[2].split("=")[1])

                # konuşalım buraları ona göre devam ettircem







            # Unlike send(), this method continues to send data from bytes until either all data has been sent or an error occurs.
            # None is returned on success.
            conn.sendall(data)










