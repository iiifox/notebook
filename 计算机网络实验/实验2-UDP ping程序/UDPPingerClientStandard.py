# UDPPingerClient.py
from socket import *
import time

serverName = '127.0.0.1'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
print(f"正在 Ping {serverName} 的数据:")
# 由于我们设置的超时值为5秒，这里可以将最小时差设置为6，这样第一次ping成功必然会刷新其值
receNum, maxDiffTime, minDiffTime, sumDiffTime = 0, -1, 6, 0
# 消息数为10
MESSAGE_NUMBER = 10
for i in range(MESSAGE_NUMBER):
    time1 = time.time()
    outputdata = f"Ping {i} {time1}"
    # 设置超时 单位秒
    clientSocket.settimeout(5)
    clientSocket.sendto(outputdata.encode(), (serverName, serverPort))
    try:
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        timeDiff = time.time() - time1
        print(f"来自 {serverName} 的回复：字节={len(outputdata)} 时间={int(1000*timeDiff)}ms")
        receNum += 1
        sumDiffTime += timeDiff
        if timeDiff > maxDiffTime:
            maxDiffTime = timeDiff
        if timeDiff < minDiffTime:
            minDiffTime = timeDiff
    except:
        print("请求超时。")
print(f"\n{serverName} 的 Ping 统计信息:")
print(f"\t数据包: 已发送 = {MESSAGE_NUMBER}, 已接收 = {receNum}, 丢失 = {10-receNum} ({int((10-receNum)*100/MESSAGE_NUMBER)}% 丢失),")
if receNum != 0:
    print("往返行程的估计时间(以毫秒为单位):")
    print(f"\t最短 = {int(1000*minDiffTime)}ms, 最长 = {int(1000*maxDiffTime)}ms, 平均 = {int(1000*sumDiffTime/receNum)}ms")
