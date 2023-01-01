
def splitURL(url)          :
    # split the url to get the function type and the name
    requestLine=url.split("\n")[0]     
    funcType= requestLine.split("?")[0].split(" ")[1]
    
    # check the function type is /favicon.ico
    if funcType == "/favicon.ico":
        name = "favicon.ico"
    else: 
        name=requestLine.split(" ")[1].split("=")[1]    

    # check the name is end with ~
    if name[-1] == "~":
        # remove the ~
        name = name[:-1]
    requestLine = requestLine.split(" ")[1]
    return requestLine,funcType,name


def responseMessageFormat(status, title, bodyMessage):


    response  =  b"HTTP/1.1 " + status + b"\n\n"
    response +=  b"Content-Type: text/plain\r\nContent-Length: {length}\r\n"     
    response +=  b"<html>"
    response +=  b"<head><title>" + title + b"</title></head>"
    response +=  b"<body>" + bodyMessage + b"</body>"                
    response +=  b"</html>"
    
    return response

def responseFormatter(status, title, bodyMessage):

    status_line = "HTTP/1.1 {status}\r\n".format(status=status)
    headers = "Content-Type: text/html\r\nContent-Length: {length}\r\n"
    body = "<html><head><title>{title}</title></head><body>{body}</body></html>"
    body = body.format(title=title, body=bodyMessage)
    headers = headers.format(length=len(body))
    response = "{status_line}{headers}\r\n{body}".format(status_line=status_line, headers=headers, body=body)
    # Encode the HTTP response as a bytes object
    return response.encode()


    