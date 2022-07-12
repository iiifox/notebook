from socket import *
import sys
import os

if len(sys.argv) <= 1:
    print(
        'Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    sys.exit(2)
# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerPort = int(sys.argv[1])
tcpSerSock.bind(("", tcpSerPort))
print(tcpSerPort)
tcpSerSock.listen(10)

while 1:
    # Strat receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    message = tcpCliSock.recv(1024).decode()
    if(message == ''):
        continue

    # Extract the filename from the given message
    print("URL:", message.split()[1])
    filename = message.split()[1].partition("//")[2]
    print("filename:", filename)
    fileExist = False

    try:
        # Check wether the file exist in the cache
        f = open(filename, "rb")
        outputdata = f.read()
        f.close()
        fileExist = True
        # ProxyServer finds a cache hit and generates a response message
        tcpCliSock.send("HTTP/1.1 200 OK\r\n".encode())
        tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
        tcpCliSock.send(outputdata)
        print('Read from cache')

    # Error handling for file not found in cache
    except IOError:
        if not fileExist:
            # Create a socket on the proxyserver
            c = socket(AF_INET, SOCK_STREAM)
            try:
                # Connect to the socket to port 80
                serverName = message.split()[1].partition(
                    "//")[2].partition("/")[0]
                serverPort = 80
                print((serverName, serverPort))
                c.connect((serverName, serverPort))

                URI = ''.join(filename.partition('/')[1:])
                print("URI:", URI)

                # Create a temporary file on this socket and ask port 80
                # for the file requested by the client
                fileobj = c.makefile('rwb', 0)
                fileobj.write(
                    f"GET {URI} HTTP/1.1\r\nHost: {serverName}:{serverPort}\r\n\r\n".encode())
                # Read the response into buffer
                serverResponse = fileobj.read()

                if serverResponse.split()[1] == b'404':
                    print('404')
                    tcpCliSock.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
                    tcpCliSock.close()
                    continue

                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socket and the corresponding file in the cache
                filesplit = filename.split('/')
                for i in range(0, len(filesplit) - 1):
                    if not os.path.exists("/".join(filesplit[0:i+1])):
                        os.makedirs("/".join(filesplit[0:i+1]))

                tmpFile = open(filename, "wb")
                serverResponse = serverResponse.split(b'\r\n\r\n')[1]
                tmpFile.write(serverResponse)
                tmpFile.close()

                tcpCliSock.send("HTTP/1.1 200 OK\r\n".encode())
                tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
                tcpCliSock.send(serverResponse)
            except:
                print("Illegal request")
            c.close()
        else:
            # HTTP response message for file not found
            print("NET ERROR")
    # Close the client and the server sockets
    tcpCliSock.close()
tcpSerSock.close()
