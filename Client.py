import socket

HOST = "127.0.0.1"  # the server's hostname or IP address
PORT = 9999  # the port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # request = b"GET / HTTP/1.1\r\nHOST\r\n\r\n"
    # sent = 0
    # while sent < len(request):
    #     sent = sent + s.send(request[sent:])  # Send a portion of 'request', starting from 'sent' byte
   # s.send(b"GET / HTTP/1.1\r\nHOST\r\n\r\n")
    s.sendall(b"/checkavailability?name=bhdr&day=8")
    # sock.send(b"GET / HTTP/1.1\r\nHost:www.example.com\r\n\r\n")
    data = s.recv(1024)


    # GET 
    # DELETE 
    # POST
print(f"Received {data!r}")