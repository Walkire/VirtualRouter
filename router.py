#!/usr/bin/env python2
"""
router.py

@Authors
Nathan Allvin
Wesley Guthrie
Bekah Suttner
"""
import re
import socket
import sys
import struct
import numpy
import netifaces as ni
from uuid import getnode as get_mac #to get mac address
from utils import itobl, htobl, bltoh #see utils.py

ETH_P_ALL = 3
BROADCAST = '0xffffffffffff'
ARP_PACKET_TYPE = '0x806'
ICMP_PACKET_TYPE = '0x800'
ROUTER_MAC = hex(get_mac())[:-1]
SOCKFD = 0

def handleARP(aData):
    print("ARP Packet found, building response")

    #Break apart ARP request
    tarMAC = aData[0:6]
    ethDst = aData[6:12]
    srcIP = aData[38:42]
    ourMAC = htobl(ROUTER_MAC)
    ethType = htobl(ARP_PACKET_TYPE)
    opCode = htobl('0x0002')
    tarIP = htobl('0x0a010003') #TODO Change to dynamic

    #replace with new values
    response = aData
    response[0:6] = ethDst
    response[6:12] = ourMAC
    response[12:14] = ethType
    response[20:22] = opCode
    response[22:28] = ourMAC
    response[28:32] = srcIP
    response[32:38] = tarMAC
    response[38:42] = tarIP

    sendStr = ''.join(str(s) for s in response)
    SOCKFD.send(sendStr)

    print("Sent ARP response")

def handleICMP(aData):
    print("ICMP Packet found, building response")

    #Break apart ICMP request
    ethDst = aData[6:12]
    srcIP = aData[30:34]
    ourMAC = htobl(ROUTER_MAC)
    tarIP = htobl('0x0a010003') #TODO Change to dynamic
    zero = htobl('0x00')

    #replace with new values
    response = aData
    response[0:6] = ethDst
    response[6:12] = ourMAC
    response[26:30] = srcIP
    response[30:34] = tarIP
    response[34] = zero

    #checksum
    response[24:26] = htobl('0x0000')
    ipHeader = ''.join(response[14:34])
    response[24:26] = checksum(ipHeader)

    sendStr = ''.join(str(s) for s in response)
    SOCKFD.send(sendStr)

    print("Sent ICMP response")


#@Author Kevin Jacobs
#http://bit.ly/2gQPkT9
def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

#@Author Kevin Jacobs
#http://bit.ly/2gQPkT9
def checksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)

    result = itobl(~s & 0xffff)
    return result[::-1] #Reverses List

def decodePacket(dataReceived):
    global BROADCAST
    global ARP_PACKET_TYPE
    global ICMP_PACKET_TYPE
    global ROUTER_MAC

    aData = list(dataReceived) #Array(list) of all byte characters
    destination = bltoh(aData[0:6])
    packetType = bltoh(aData[12:14])

    if destination == ROUTER_MAC or destination == BROADCAST:
        #this packet is for us
        if packetType == ARP_PACKET_TYPE:
            handleARP(aData)
        elif packetType == ICMP_PACKET_TYPE:
            handleICMP(aData)

def main():
    global ETH_P_ALL
    global SOCKFD
    SOCKFD = socket.socket()
    eth1_interfaces = []

    # get all interfaces that match the r?-eth1 format (see line 27 in route.c)
    print("Interfaces: {0}".format(str(ni.interfaces())))
    for interface in ni.interfaces():
        if interface[3:] == "eth1":
            eth1_interfaces.append(interface)

    print("Interfaces: {}".format(str(eth1_interfaces)))

    for i in eth1_interfaces:
        # get the addresses associated with this interface
        address = ni.ifaddresses(i)
        # get the packet address associated with it
        eth1_packet_address = address[ni.AF_PACKET][0]['addr']
        print("eth1_packet_address: {}".format(str(eth1_packet_address)))

        # python string interpolation
        print("Creating socket on interface {}".format(i))

        # create the packet socket
        try:
            SOCKFD = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
        except:
            print ('Socket could not be created')
            sys.exit()
        # bind the packet socket to this interface
        SOCKFD.bind((i, 0))


    while True:
        dataReceived, address = SOCKFD.recvfrom(1024)
        print("Got a {0} byte packet from {1}:{2}".format(len(dataReceived), address[0], address[1]))
        decodePacket(dataReceived)


if __name__ == '__main__':
    main()
