import socket

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
            print("data: ", data)



            url= data.decode("utf-8")

            print("The url is", url)
            
            
            funcType= url.split("?")[0]
            name=url.split("?")[1].split("=")[1]

            print("fucntType", funcType,"\nname", name)
            

            if funcType == "/add":
                print("add")
                # check the room name exist on the room.txt file 
                # if it is not exist, then add the name to the room.txt file
                # if it is exist, then print the error message
                
                lines = []
                file = open("rooms.txt", 'r')    
                for line in file:
                    lines.append(line.strip())

                for line in lines:
                    print(line)
                    
                if lines.__contains__(name):
                    print("The room name is already exist")
                else:
                    print("The room name is not exist")
                    
                    file.write(name)
                    file.write("\n")
                    print("The room name is added to the file")
                    file.close()
                                
            elif funcType == "/remove":
                print("remove")

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
            

                
            elif funcType == "/reserve":
                print("reserve")                    

            # Unlike send(), this method continues to send data from bytes until either all data has been sent or an error occurs.
            # None is returned on success.
            conn.sendall(data)



        # /add?name=activityname
        # /remove?name=activityname: 
        # /reserve?name=roomname&day=x&hour=y&duration=z

        # /check?name=activityname
