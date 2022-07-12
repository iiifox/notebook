from socket import *
import sys
import os

if len(sys.argv) <= 1:
    print(
        'Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    sys.exit(2)
# 创建socket，绑定到端口，开始监听
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerPort = int(sys.argv[1])
tcpSerSock.bind(("", tcpSerPort))
tcpSerSock.listen(10)

while 1:
    # 开始从客户端接收请求
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    # 请求信息
    message = tcpCliSock.recv(1024).decode()
    if message == '':
        continue

    # 请求的URL
    print("URL:", message.split()[1])
    # 从请求中解析出文件名
    filename = message.split()[1].partition("//")[2]
    print("filename:", filename)
    fileExist = False

    try:
        # 检查缓存中是否存在该文件
        f = open(filename, "rb")
        outputdata = f.read()
        f.close()
        fileExist = True
        # 代理服务器缓存中存在该文件，向客户端中发送响应消息
        tcpCliSock.send("HTTP/1.1 200 OK\r\n".encode())
        tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
        tcpCliSock.send(outputdata)
        print('Read from cache')

    # 缓存中不存在该文件，异常处理
    except IOError:
        # open报错-->文件没找到异常
        if not fileExist:
            # 在代理服务器上创建一个socket
            c = socket(AF_INET, SOCK_STREAM)
            try:
                # 连接到远程服务器80端口
                serverName = message.split()[1].partition(
                    "//")[2].partition("/")[0]
                serverPort = 80
                print((serverName, serverPort))
                c.connect((serverName, serverPort))

                # 请求资源的URI
                URI = ''.join(filename.partition('/')[1:])
                print("URI:", URI)

                # 在这个套接字上创建一个临时文件，并请求端口号80来获取客户机请求的文件
                fileobj = c.makefile('rwb', 0)
                # 请求信息:请求行+请求头+空白行+请求体
                fileobj.write(
                    f"GET {URI} HTTP/1.1\r\nHost: {serverName}:{serverPort}\r\n\r\n".encode())
                # 将响应读入缓冲区
                serverResponse = fileobj.read()

                # 在缓存中为请求的文件创建一个新文件。
                # 还将缓冲区中的响应发送给客户端套接字和缓存中的相应文件
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
            # 找不到文件的HTTP响应消息
            print("NET ERROR")
    # 关闭客户端和服务器套接字
    tcpCliSock.close()
tcpSerSock.close()
