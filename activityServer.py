import socket
import os.path

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
            url = data.decode("utf-8")
            print("The url is", url)

            funcType = url.split("?")[0]
            print("The functype is", funcType)

            name = url.split("?")[1].split("=")[1]
            print("The name is", name)

            if funcType == "/add":
                lines = []
                control = 0
                if os.path.exists('activities.txt'):
                    file = open("activities.txt", 'r')
                    for line in file:
                        if(name == line.strip()):
                            # print("The activity name is already exist 403 atilcak")
                            conn.sendall(b"HTTP/1.1 403 Forbidden\n")
                            control = 1
                            break
                    file.close()

                if(control == 0):
                    file = open("activities.txt", 'a')
                    file.write(name)
                    file.write("\n")
                    conn.sendall(
                        b"HTTP/1.1 200 OK\n" +
                        b"Content-Type: text/html\n" +
                        b"\n")
                    # print("The activity name is added to the file")
                    file.close()

            elif funcType == "/remove":
                if os.path.exists('activities.txt'):
                    lines = []
                    file = open("activities.txt", 'r')
                    for line in file:
                        lines.append(line.strip())

                    file.close()

                    if not lines.__contains__(name):
                        conn.sendall(b"HTTP/1.1 403 Forbidden\n")
                        # print("The activity name is  not exist")
                    else:
                        conn.sendall(
                            b"HTTP/1.1 200 OK\n" +
                            b"Content-Type: text/html\n" +
                            b"\n")
                        # print("The activity name is  exist")

                        file = open("activities.txt", 'w')
                        file.seek(0)
                        lines.remove(name)
                        for line in lines:
                            file.write(line)
                            file.write("\n")
                        file.close()
                else:
                    conn.sendall(b"HTTP/1.1 404 Not Found\n")
                    # print("file not exists.")

            elif funcType == "/check":
                print ("--------- check---------")
                if os.path.exists('activities.txt'):
                    control = 0
                    file = open("activities.txt", 'r')
                    for line in file:
                        if(line.strip() == name):
                            conn.sendall(
                                b"HTTP/1.1 200 OK\n" +
                                b"Content-Type: text/html\n" +
                                b"\n")
                            print("There exists activity")
                            control = 1
                            break
                    if(control == 0):
                        conn.sendall(b"HTTP/1.1 404 Not Found\n")
                        print("not found in activity.txt")
                    file.close()
                else:
                    conn.sendall(b"HTTP/1.1 404 Not Found\n") #i think not necessary
                    print("activity.txt file does not exist")

            else:
                conn.sendall(b"HTTP/1.1 400 Bad Request\n")
