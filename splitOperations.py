
def splitURL(url)          :
    
    if(url.__contains__("\n")):
        requestLine=url.split("\n")[0]     
    else:
        requestLine=url

    if(requestLine.__contains__("?")):
        funcType= requestLine.split("?")[0]
        if(funcType.__contains__(" ")):
            funcType=funcType.split(" ")[1]
        else:
            funcType=funcType
    else:
        funcType = "/invalid"
    
    
    # check the function type is /favicon.ico
    if funcType == "/favicon.ico":
        # read the referer line from the request
        name=url.split("Referer: ")[1].split("\n")[0].split("localhost")[1].split("/")[1].split("?")[0]
        #  add \ to the start of the name
        name="\\"+name
        
    
    else: 
        if(requestLine.__contains__(" ")):
            name=requestLine.split(" ")[1]
            if(name.__contains__("=")):
                name=name.split("=")[1]
            else:
                name=name
        else:
            name = "invalid"



    if name[-1] == "~":
        name = name[:-1]
    if(requestLine.__contains__(" ")):
        requestLine = requestLine.split(" ")[1]
    else:
        requestLine = "invalid"
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


    