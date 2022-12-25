import socket

HOST = "localhost"  # The server's hostname or IP address

PORT = 8083  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind((HOST, PORT)) 
        s.listen() # if you put any number in this function ex: 5, it means that it will listen 5 connections after that it is going to throw an error
        conn, addr = s.accept()
        
    
       # get the request from the client
        request = s.recv(1024)
        print("The request is", request)

        # send the response to the client
        s.sendall(b"HTTP/1.1 200 OK\n" +
                    b"Content-Type: text/html\n" +
                    b"\n" +
                    b"Hello, World!")
        
        # close the connection
        s.close()





        



