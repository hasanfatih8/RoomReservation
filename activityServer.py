import socket
import os.path
from splitOperations import *

HOST = "localhost"
PORT = 8082

# with command, we don't need to use try catch blocks

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen()  # if you put any number in this function ex: 5, it means that it will listen 5 connections after that it is going to throw an error
    while True:
        # connection object will be stored in conn, list of ip addresses will be storedin addr
        conn, addr = s.accept()

        with conn:
            print(f"Connected by {addr}")

            # take the first 1024 byte, other than that can be junk
            data = conn.recv(1024)
            if not data:
                break
            # Check if the request is for the favicon
            if b"favicon.ico" in data:
            # Ignore the request and do not send a response
                pass
            url = data.decode("utf-8")
            print("The url is", url)

            # split the url to get the function type and the name
            requestLine,funcType,name=splitURL(url)
            print("The request line is", requestLine)
            print("The function type is", funcType)
            print("The name is", name)

            # Add activity to server
            if funcType == "/add":
                lines = []
                control = 0
                # check if the file exists
                if os.path.exists('activities.txt'):
                    file = open("activities.txt", 'r')
                    for line in file:
                        if(name == line.strip()):
                            # print("The activity name is already exist 403 atilcak")
                            # Return 403 Forbidden if activity already exists
                            response = responseFormatter("403 Forbidden", "Already", f"Activity {name} already exist.")
                            conn.sendall(response)
                            #conn.sendall(b"HTTP/1.1 403 Forbidden\n")
                            control = 1
                            break
                    file.close()
                # .If activity does not exist, add it to server and return 200 OK
                if(control == 0):
                    file = open("activities.txt", 'a')
                    file.write(name)
                    file.write("\n")
                    response = responseFormatter("200 OK", "Add Activity", f"Activity {name} is added.")
                    conn.sendall(response)
                    # print("The activity name is added to the file")
                    file.close()
            
            # Remove activity from server
            elif funcType == "/remove":
                if os.path.exists('activities.txt'):
                    lines = []
                    file = open("activities.txt", 'r')
                    for line in file:
                        lines.append(line.strip())

                    file.close()
                    # Return 403 Forbidden if activity does not exist
                    if not lines.__contains__(name):
                        response = responseFormatter("403 Forbidden", "Remove Activity", f"Activity {name} does not exist.")
                        conn.sendall(response)
                        
                    # If activity exists, remove it from server and return 200 OK
                    else:
                        """
                        conn.sendall(
                            b"HTTP/1.1 200 OK\n" +
                            b"Content-Type: text/html\n" +
                            b"\n")
                        """
                        file = open("activities.txt", 'w')
                        file.seek(0)
                        lines.remove(name)
                        for line in lines:
                            file.write(line)
                            file.write("\n")
                        file.close()
                        response = responseFormatter("200 OK", "Remove Activity", f"Activity {name} is removed successfully.")
                        conn.sendall(response)
                # If file does not exist, return 404 Not Found
                else:
                    response = responseFormatter("404 Not Found", "Remove Activity", f"File doesn't exist.")
                    conn.sendall(response)
                    
            # Check if activity exists in server
            elif funcType == "/check":
                print ("--------- check---------")
                if os.path.exists('activities.txt'):
                    control = 0
                    file = open("activities.txt", 'r')
                    for line in file:
                        if(line.strip() == name):
                            response = responseFormatter("200 OK", "Check Activity", f"Activity {name} exists")
                            conn.sendall(response)
                            """
                            conn.sendall(
                                b"HTTP/1.1 200 OK\n" +
                                b"Content-Type: text/html\n" +
                                b"\n")
                            """
                            print("There exists activity")
                            control = 1
                            break
                    if(control == 0):
                        response = responseFormatter("404 Not Found", "Check Activity", f"Activity {name} does not exist")
                        conn.sendall(response)
                        #conn.sendall(b"HTTP/1.1 404 Not Found\n")
                        # print("not found 404 dön")
                    file.close()
                else:
                    response = responseFormatter("404 Not Found", "Check Activity", f"404 Not Found")
                    conn.sendall(response)
                    #conn.sendall(b"HTTP/1.1 404 Not Found\n")
                    # print("file not exists.")

            else:
                response = responseFormatter("400 Bad Request", "Bad Request", f"Bad Requestxd")
                conn.sendall(response)
                #conn.sendall(b"HTTP/1.1 400 Bad Request\n")
