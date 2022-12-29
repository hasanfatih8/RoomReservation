
def splitURL(url)          :
    
    requestLine=url.split("\n")[0]     
    funcType= requestLine.split("?")[0].split(" ")[1]
    
    # check the function type is /favicon.ico
    if funcType == "/favicon.ico":
        name = "favicon.ico"
    else: 
        name=requestLine.split(" ")[1].split("=")[1]    



    if name[-1] == "~":
        name = name[:-1]
    requestLine = requestLine.split(" ")[1]
    return requestLine,funcType,name


def responseMessageFormat(statu,title,bodyMessage):


    response  =  b"HTTP/1.1 "+statu+b"\n"
    response +=  b"Content-Type: text/html\n\n"     
    response +=  b"<html>"
   # response +=  b"<head><title>"+title+b"</title></head>"
    response +=  b"<body>"+bodyMessage+b"</body>"                
    response +=  b"</html>"
    
    return response

    