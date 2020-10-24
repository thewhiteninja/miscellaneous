#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import struct
import time
import random

from modules.logger import *

ICMP_ECHO_REQUEST = 8
DESTINATION_REACHED = 1
SOCKET_TIMEOUT = 2
TIME_LIMIT_EXCEEDED = 11
ECHO_REPLY = 0

if sys.platform == "win32":
    default_timer = time.clock
else:
    default_timer = time.time


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


def buildpacket(packettype, size):
    my_checksum = 0
    anid = random.randint(0, 0xFFFF)
    header = struct.pack("bbHHh", packettype, 0, my_checksum, anid, 1)
    bytesindouble = struct.calcsize("d")
    data = (size - bytesindouble) * "Q"
    data = struct.pack("d", default_timer()) + data
    my_checksum = checksum(header + data)
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, anid, 1
    )
    return header + data, anid

def ping(destaddr, timeout, ttl):
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    mysocket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    mysocket.settimeout(timeout)

    packet, pid = buildpacket(ICMP_ECHO_REQUEST, 8)
    mysocket.sendto(packet, (destaddr, 1))

    res = None, None, SOCKET_TIMEOUT
    starttime = default_timer()
    while (default_timer() - starttime) < timeout:
        try:
            recpacket, (addr, x) = mysocket.recvfrom(1024)
        except socket.timeout:
            break
        timereceived = default_timer()
        icmptype, code = struct.unpack("bb", recpacket[20:22])
        if icmptype == TIME_LIMIT_EXCEEDED:
            res = timereceived - starttime, addr, None
            break
        elif icmptype == ECHO_REPLY:
            res = timereceived - starttime, addr, DESTINATION_REACHED
            break
    mysocket.close()
    return res


def traceroute(host, timeout, maxhops):
    route = []
    dest = socket.gethostbyname(host)
    for ttl in range(1, maxhops + 1):
        point = [ttl]
        addr = False
        info = None
        for i in range(2):
            delay, address, info = ping(dest, timeout, ttl)
            if delay and not addr:
                try:
                    h, _, _ = socket.gethostbyaddr(address)
                except socket.herror:
                    h = address
                point.insert(1, address)
                point.insert(1, h)
                addr = True
            point.append(delay)
        route.append(point)
        if info == DESTINATION_REACHED:
            break
    return host, route
