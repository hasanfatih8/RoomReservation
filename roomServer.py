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
                            

            # Unlike send(), this method continues to send data from bytes until either all data has been sent or an error occurs.
            # None is returned on success.
            conn.sendall(data)



        # /add?name=activityname
        # /remove?name=activityname: 
        # /check?name=activityname