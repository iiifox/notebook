from socket import *
import base64


# Choose a mail server (e.g. Google mail server) and call it mailserver
mailserver = "smtp.qq.com"
# 发送方地址和接收方地址，from 和 to
mailFromAddress = 'tianzhang.chn@qq.com'
mailToAddress = 'tianzhang.chn@gmail.com'
# 用户名,由于我们指定了邮箱服务器为qq,因此是可以省略后缀的,当然也可以用mailFromAddress
username = mailFromAddress
# 此处不是自己的密码，而是开启SMTP服务时对应的授权码
password = 'ybtlpzfewslqdcdi'

# Create socket called clientSocket and establish a TCP connection with mailserver
'''
(class) socket(family: AddressFamily | int = ..., type: SocketKind | int = ..., proto: int = ..., fileno: int | None = ...)
family(给定的套接族)一般有两种重要参数：
    socket.AF_INET	用于服务器与服务器之间的网络通信
    socket.AF_INET6	基于IPV6方式的服务器与服务器之间的网络通信
type(套接字类型)，也是一般两个类型：
    socket.SOCK_STREAM	基于TCP的流式socket通信
    socket.SOCK_DGRAM	基于UDP的数据报式socket通信
'''
clientSocket = socket(AF_INET, SOCK_STREAM)
# 常用邮箱的服务器(SMTP/POP3)地址和端口整理 https://blog.51cto.com/u_15300443/3091999
# 或者由于我们直接进QQ邮箱官网 https://service.mail.qq.com/cgi-bin/help?subtype=1&id=20010&no=1000557
# 因此端口号我们选择25
serverPort = 25
# connect只能接收一个参数
clientSocket.connect((mailserver, serverPort))

# 从客户套接字中接收信息
# 220 服务就绪，可以执行新用户的请求。
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '220':
    print('220 reply not received from server.')

# Send HELO command and print server response.
# 开始与服务器的交互，服务器将返回状态码250,说明请求动作正确完成
heloCommand = 'HELO mailserver\r\n'
clientSocket.send(heloCommand.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '250':
    print('250 reply not received from server.')

# 发送"AUTH LOGIN"命令，验证身份.服务器将返回状态码334（服务器等待用户输入验证信息）
loginCommand = 'AUTH LOGIN\r\n'
clientSocket.send(loginCommand.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '334':
    print('334 reply not received from server.')

# 邮箱账户经过base64编码
# base64编码后是一些bytes字符串,因此我们加换行符也需要+ b'\r\n'
userCommand = base64.b64encode(username.encode()) + b'\r\n'
clientSocket.send(userCommand)
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '334':
    print('334 reply not received from server')

# 邮箱密码经过base64编码
passCommand = base64.b64encode(password.encode()) + b'\r\n'
clientSocket.send(passCommand)
recv = clientSocket.recv(1024).decode()
print(recv)
# 如果用户验证成功，服务器将返回状态码235
if recv[:3] != '235':
    print('235 reply not received from server')

# Send MAIL FROM command and print server response.
# TCP连接建立好之后，通过用户验证就可以开始发送邮件。邮件的传送从MAIL命令开始，MAIL命令后面附上发件人的地址。
# 发送 MAIL FROM 命令，并包含发件人邮箱地址
MFCommand = 'MAIL FROM: <'+ mailFromAddress + '>\r\n'
clientSocket.send(MFCommand.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '250':
    print('250 reply not received from server.')

# Send RCPT TO command and print server response.
# 接着SMTP客户端发送一个或多个RCPT (收件人recipient的缩写)命令，格式为RCPT TO: <收件人地址>。
# 发送 RCPT TO 命令，并包含收件人邮箱地址，返回状态码 250
RTCommand = 'RCPT TO: <'+ mailToAddress + '>\r\n'
clientSocket.send(RTCommand.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '250':
    print('250 reply not received from server.')

# Send DATA command and print server response.
# 发送 DATA 命令，表示即将发送邮件内容。服务器将返回状态码354（开始邮件输入，以"."结束）
DATACommand = 'DATA\r\n'
clientSocket.send(DATACommand.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '354':
    print('354 reply not received from server.')

# Send message data.
msg = 'From: ' + mailFromAddress + '\r\n'
msg += 'To: ' + mailToAddress +  '\r\n'
msg += 'Subject: ' + '测试' +  '\r\n'
msg += "\r\n I love computer networks!"
clientSocket.send(msg.encode())

# Message ends with a single period.
# 以"."结束。请求成功返回 250
endmsg = "\r\n.\r\n"
clientSocket.send(endmsg.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '250':
    print('250 reply not received from server.')

# Send QUIT command and get server response.
QUITCommand = 'QUIT\r\n'
clientSocket.send(QUITCommand.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
# 221 服务关闭控制连接。
if recv[:3] != '221':
    print('221 reply not received from server.')

clientSocket.close()
