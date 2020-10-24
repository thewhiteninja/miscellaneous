#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
import struct
import select
import time
import random

if sys.platform == "win32":
    default_timer = time.clock
else:
    default_timer = time.time

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
ICMP_TIMESTAMP_REQUEST = 13
ICMP_TIMESTAMP_REPLY = 14
ICMP_MASK_REQUEST = 17
ICMP_MASK_REPLY = 18


def checksum(source_string):
    asum = 0
    countto = (len(source_string) / 2) * 2
    count = 0
    while count < countto:
        thisval = ord(source_string[count + 1]) * 256 + ord(source_string[count])
        asum += thisval
        asum &= 0xffffffff  # Necessary?
        count += 2
    if countto < len(source_string):
        asum += ord(source_string[len(source_string) - 1])
        asum &= 0xffffffff  # Necessary?
    asum = (asum >> 16) + (asum & 0xffff)
    asum += asum >> 16
    answer = ~asum
    answer &= 0xffff
    return answer


def receive_one_ping(my_socket, ID, timeout, type_sent):
    timeLeft = timeout
    while True:
        startedSelect = default_timer()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = (default_timer() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return None

        timeReceived = default_timer()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:26]
        type, code, checksum, packetID = struct.unpack(
            "bbHH", icmpHeader
        )

        bytesInDouble = struct.calcsize("d")
        if type_sent == ICMP_ECHO_REQUEST and type == ICMP_ECHO_REPLY and packetID == ID:
            timesent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timesent
        elif type_sent == ICMP_TIMESTAMP_REQUEST and type == ICMP_TIMESTAMP_REPLY and packetID == ID:
            return struct.unpack(">LLL", recPacket[28:40])
        elif type_sent == ICMP_MASK_REQUEST and type == ICMP_MASK_REPLY and packetID == ID:
            return struct.unpack("L", recPacket[28:32])

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return None


def buildpacket(packettype, size=32):
    my_checksum = 0
    anid = random.randint(0, 0xFFFF)
    header = struct.pack("bbHHh", packettype, 0, my_checksum, anid, 1)

    if packettype == ICMP_ECHO_REQUEST:
        data = struct.pack("d", default_timer())
        data += (size - len(data)) * "Q"
    elif packettype == ICMP_TIMESTAMP_REQUEST:
        data = struct.pack("ddd", 0, 0, 0)
    elif packettype == ICMP_MASK_REQUEST:
        data = struct.pack("d", 0)

    my_checksum = checksum(header + data)
    header = struct.pack(
        "bbHHh", packettype, 0, my_checksum, anid, 1
    )
    return header + data, anid


def create_icmp_socket(dest_addr):
    icmp = socket.getprotobyname("icmp")
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    dest_addr = socket.gethostbyname(dest_addr)
    return my_socket, dest_addr


def ping(ping_type, dest_addr, timeout, size=32):
    try:
        my_socket, dest_addr = create_icmp_socket(dest_addr)

        packet, pid = buildpacket(ping_type, size)
        my_socket.sendto(packet, (dest_addr, 1))
        res = receive_one_ping(my_socket, pid, timeout, ping_type)

        my_socket.close()
        return res
    except socket.gaierror, e:
        return None
