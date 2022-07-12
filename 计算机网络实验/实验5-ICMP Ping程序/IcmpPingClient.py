import socket
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8


def checksum(strCheck):
    '''校验和'''
    csum = 0
    countTo = (len(strCheck) / 2) * 2
    count = 0
    while count < countTo:
        thisVal = strCheck[count + 1] * 256 + strCheck[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(strCheck):
        csum = csum + strCheck[len(strCheck) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    '''收到一个 Ping'''
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # 从IP报文中获取ICMP头
        header = recPacket[20:28]
        header_type, header_code, header_checksum, header_packet_ID, header_sequence = struct.unpack(
            "bbHHh", header)

        if (header_type != 0 or header_code != 0 or header_packet_ID != ID or header_sequence != 1):
            return "Receive error."

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."
        return timeLeft


def sendOnePing(mySocket, destAddr, ID):
    '''发送一个 ping'''
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # 创建一个校验和为0的虚拟头。
    # struct——将字符串解释为压缩的二进制数据
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # 计算数据和虚拟头的校验和。
    myChecksum = checksum(header + data)

    # 得到正确的校验和，并放入头部
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff
        # 将16位整数从主机字节顺序转换为网络字节顺序。
    else:
        myChecksum = socket.htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))  # AF_INET地址必须是元组，而不是str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object


def doOnePing(destAddr, timeout):
    '''做一个 ping'''
    icmp = socket.getprotobyname("icmp")

    # SOCK_RAW是一个强大的套接字类型。更多信息请参见:http://sock-raw.org/papers/sock_raw
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # 返回当前进程i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay


def ping(host, timeout=1):
    '''向 host 主机发送一个 ping 请求, 默认超时时长为 1s'''
    # timeout=1的意思是:如果一秒钟没有收到服务器的回复，客户端就会认为客户端的ping或者服务器的pong丢失了
    dest = socket.gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")

    # 向间隔大约一秒的服务器发送ping请求
    for i in range(4):
        delay = doOnePing(dest, timeout)
        print(delay)
        # 睡眠一秒钟
        time.sleep(1)


ping("www.hutb.edu.cn")
