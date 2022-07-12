from socket import *
import base64
import ssl


# Choose a mail server (e.g. Google mail server) and call it mailserver
mailserver = "smtp.qq.com"
mailFromAddress = 'tianzhang.chn@qq.com'
mailToAddress = 'tianzhang.chn@gmail.com'
username = mailFromAddress
password = 'ybtlpzfewslqdcdi'

# Create socket called clientSocket and establish a TCP connection with mailserver
# 这里使用的SSL连接,qq邮箱的SSL协议端口号是465,参考资料下方超链接
# https://service.mail.qq.com/cgi-bin/help?subtype=1&id=20010&no=1000557
serverPort=465
# 直接使用默认参数获取一个SSLContext实例
context = ssl.create_default_context()
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, serverPort))
# 封装套接字
clientSocketSSL = context.wrap_socket(clientSocket, server_hostname=mailserver)

recv = clientSocketSSL.recv(1024).decode()
print(recv)
if recv[:3] != '220':
    print('220 reply not received from server.')

# Send HELO command and print server response.
heloCommand = 'HELO mailserver\r\n'
clientSocketSSL.send(heloCommand.encode())
recv = clientSocketSSL.recv(1024).decode()
print(recv)
if recv[:3] != '250':
    print('250 reply not received from server.')

# 登录过程
loginCommand = 'AUTH LOGIN\r\n'
clientSocketSSL.send(loginCommand.encode())
recv = clientSocketSSL.recv(1024).decode()
print(recv)
if recv[:3] != '334':
    print('334 reply not received from server.')

# 邮箱账户经过base64编码
userCommand = base64.b64encode(username.encode()) + b'\r\n'
clientSocketSSL.send(userCommand)
recv = clientSocketSSL.recv(1024).decode()
print(recv)
if recv[:3] != '334':
    print('334 reply not received from server')

# 邮箱密码经过base64编码
passCommand = base64.b64encode(password.encode()) + b'\r\n'
clientSocketSSL.send(passCommand)
recv = clientSocketSSL.recv(1024).decode()
print(recv)
if recv[:3] != '235':
    print('235 reply not received from server')

# Send MAIL FROM command and print server response.
MFCommand = 'MAIL FROM: <'+ mailFromAddress + '>\r\n'
clientSocketSSL.send(MFCommand.encode())
recv = clientSocketSSL.recv(1024).decode()
print(recv)
if recv[:3] != '250':
    print('250 reply not received from server.')

# Send RCPT TO command and print server response.
RTCommand = 'RCPT TO: <'+ mailToAddress + '>\r\n'
clientSocketSSL.send(RTCommand.encode())
recv = clientSocketSSL.recv(1024).decode()
print(recv)
if recv[:3] != '250':
    print('250 reply not received from server.')

# Send DATA command and print server response.
DATACommand = 'DATA\r\n'
clientSocketSSL.send(DATACommand.encode())
recv = clientSocketSSL.recv(1024).decode()
print(recv)
if recv[:3] != '354':
    print('354 reply not received from server.')

# Send message data.
msg = 'From: ' + mailFromAddress + '\r\n'
msg += 'To: ' + mailToAddress +  '\r\n'
msg += 'Subject: ' + '测试' +  '\r\n'
msg += "\r\n I love computer networks!"
clientSocketSSL.send(msg.encode())

# Message ends with a single period.
endmsg = "\r\n.\r\n"
clientSocketSSL.send(endmsg.encode())
recv = clientSocketSSL.recv(1024).decode()
print(recv)
if recv[:3] != '250':
    print('250 reply not received from server.')

# Send QUIT command and get server response.
QUITCommand = 'QUIT\r\n'
clientSocketSSL.send(QUITCommand.encode())
recv = clientSocketSSL.recv(1024).decode()
print(recv)
if recv[:3] != '221':
    print('221 reply not received from server.')

clientSocketSSL.close()
