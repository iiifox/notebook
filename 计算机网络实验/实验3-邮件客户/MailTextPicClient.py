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
serverPort=465
context = ssl.create_default_context()
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, serverPort))
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
# 转换图片和HTML文本
with open("刘亦菲.jpg","rb") as f:
    image_data = base64.b64encode(f.read())
with open("hello.html","rb") as f:
    html_data = base64.b64encode(f.read())


# 构造邮件正文 参考文档 http://niehan.blog.techweb.com.cn/archives/250.html
msg = 'FROM: ' + mailFromAddress + '\r\n'
msg += 'TO: ' + mailToAddress +  '\r\n'
msg += 'Subject:超文本和图片\r\n'
'''
+----------------------------------------multipart/mixed----------------------------------------+
|                                                                                               |
|                                                                                               |
|   +---------------------------multipart/related---------------------------+                   |
|   |                                                                       |                   |
|   |                                                                       |                   |
|   |   +---------mutipart/alternative--------------+   +-------------+     |   +-------+       |
|   |   |                                           |   |   内嵌资源   |     |   |  附件  |       |
|   |   |                                           |   +-------------+     |   +-------+       |
|   |   |   +---------------+   +---------------+   |                       |                   |
|   |   |   |   纯文本正文   |   |   超文本正文    |   |                       |                   |
|   |   |   +---------------+   +---------------+   |   +-------------+     |   +-------+       |
|   |   |                                           |   |   内嵌资源   |     |   |  附件  |       |
|   |   |                                           |   +-------------+     |   +-------+       |
|   |   +-------------------------------------------+                       |                   |
|   |                                                                       |                   |
|   |                                                                       |                   |
|   +-----------------------------------------------------------------------+                   |
|                                                                                               |
|                                                                                               |
+-----------------------------------------------------------------------------------------------+
'''
# 这里我们使用了超文本和图片，因此需要设置 Content-Type:multipart/related
# boundary参数取值 https://www.vlts.cn/posts/28d1c9d8.html
'''
请求头的Content-Type属性除了指定为multipart/related, 还需要定义boundary属性。
    boundary的值必须以英文中间双横杠--开头，这个--称为前导连字符;
    boundary的值除了前导连字符以外的部分不能超过70个字符;
    boundary的值不能包含HTTP协议或者URL禁用的特殊意义的字符。

    请求体中的请求行数据是由多部分组成, boundary属性的值模式--${boundary}用于分隔每个独立的分部。
    每个部分可以单独定义Content-Type和该部分的数据体
    请求体以boundary参数的值模式--${boundary}--作为结束标志

    每个--${boundary}之前默认强制必须为CRLF,
    如果某一个部分的文本类型请求体以CRLF结尾,那么在请求体的二级制格式上,必须显式存在两个CRLF,
    如果某一个部分的请求体不以CRLF结尾,可以只存在一个CRLF,这两种情况分别称为分隔符的显式类型和隐式类型。

'''
msg += 'Content-Type:multipart/related; boundary="--tianzhang"\r\n'
msg += 'MIME-Version:1.0\r\n'
msg += '\r\n'
msg = msg.encode()

# html文件与图片此时已经是二进制字符串，因此我们每次添加的数据都需要进行编码发送，即不能直接添加后整体编码
# 添加html文件
msg += '----tianzhang\r\n'.encode()
# content-type的各种取值 https://www.runoob.com/http/http-content-type.html
msg += 'Content-Type:text/html; charset="UTF-8"\r\n'.encode()
'''
MIME邮件可以传送图像、声音、视频以及附件,这些非ASCII码的数据都是通过一定的编码规则进行转换后附着在邮件中进行传递的。
编码方式存储在邮件的Content-Transfer-Encoding域中,
一封邮件中可能有多个Content-Transfer-Encoding域,分别对应邮件不同部分内容的编码方式。
目前MIME邮件中的数据编码普遍采用Base64编码或Quoted-printable编码来实现。
'''
# 对二进制内容进行转换  name属性值有:7bit、8bit、binary、quoted-printable、base64
msg += 'Content-Transfer-Encoding:base64\r\n'.encode()
msg += '\r\n'.encode()
msg += html_data
msg += '\r\n'.encode()
msg += '\r\n'.encode()

# 添加图片
msg += '----tianzhang\r\n'.encode()
msg += 'Content-Type:image/jpeg; name="刘亦菲.jpg"\r\n'.encode()
msg += 'Content-Transfer-Encoding:base64\r\n'.encode()
msg += '\r\n'.encode()
msg += image_data
msg += "\r\n".encode()
msg += '\r\n'.encode()
msg += '----tianzhang--\r\n'.encode()
clientSocketSSL.send(msg)


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
