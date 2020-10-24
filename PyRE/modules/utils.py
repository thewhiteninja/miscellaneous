import os
import glob
import urllib2
import sys
import time
import platform
import struct
import hashlib

from modules.windows.defines import *
import logger
import math


class Args:

    def __init__(self):
        self.executable_filename = None


def is_executable(exe):
    if exe == "" or exe is None:
        logger.logWarn("No executable file provided")
        return False
    if not os.path.isfile(exe):
        logger.logWarn("No such file: " + exe + " from " + os.getcwd())
        return False
    if not os.access(exe, os.X_OK):
        logger.logWarn("The file is not executable. Please check the rights")
        return False
    return True


def get_executable_type(path):
    binary_type = c_ulong(0)
    windll.kernel32.GetBinaryTypeA(c_char_p(path), byref(binary_type))
    return binary_type.value


def hashFile(filename):
    f = open(filename, "rb")
    content = f.read()
    f.close()
    return hashMem(content)


def hasNull(a):
    return a & 0xff == 0 or a & 0xff00 == 0 or a & 0xff0000 == 0 or a & 0xff000000 == 0


def hasUTF8(a):
    return a & 0xff > 127 or a & 0xff00 > 127 or a & 0xff0000 > 127 or a & 0xff000000 > 127


def hashMem(mem):
    h = dict()
    a = hashlib.md5()
    a.update(mem)
    h["md5"] = a.hexdigest()
    a = hashlib.sha1()
    a.update(mem)
    h["sha1"] = a.hexdigest()
    a = hashlib.sha256()
    a.update(mem)
    h["sha256"] = a.hexdigest()
    return h


def sha1(filename):
    h = hashlib.sha1()
    f = open(filename, "rb")
    h.update(f.read())
    f.close()
    return h.hexdigest()


def md5(filename):
    h = hashlib.md5()
    f = open(filename, "rb")
    h.update(f.read())
    f.close()
    return h.hexdigest()


def clean_folder(directory):
    for f in glob.glob(directory + '/*'):
        os.remove(f)


def unicode_to_ansi(s):
    ansi = ""
    i = 0
    while i < len(s) and ord(s[i]) != 0:
        ansi += s[i]
        i += 2
    return ansi


def get_OS():
    s = platform.platform()
    if s.startswith("Windows"):
        return WINDOWS
    elif s.startswith("Linux"):
        return LINUX
    elif s.startswith("Mac"):
        return MAC
    else:
        return UNKNOWN


def is_OS_64():
    return "PROGRAMFILES(X86)" in os.environ


def is_Python_64():
    return platform.architecture()[0] == "64bit"


def welcome():
    print """
  _____       _____  ______
 |  __ \     |  __ \|  ____|
 | |__) |   _| |__) | |__   
 |  ___/ | | |  _  /|  __|  
 | |   | |_| | | \ \| |____ 
 |_|    \__, |_|  \_\______|
         __/ |              
        |___/               
    """
    print "Starting %s at %s (%s version)\n" % (
        os.path.basename(sys.argv[0]), time.asctime(time.localtime(time.time())), platform.architecture()[0])


def read_number(a):
    a = a.lower()
    if a.startswith("0x"):
        return int(a[2:], 16)
    elif a.startswith("0b"):
        return int(a[2:], 2)
    else:
        return int(a, 10)


def readNullString(mem, offset, maxlen):
    s = mem[offset:offset + maxlen].tobytes()
    zero = s.find("\x00")
    if zero:
        return s[:zero]
    return s


def xor(a, b):
    if type(a) is str and type(b) is str:
        if len(b) < len(a):
            b *= (len(a) / len(b)) + 1
        return "".join([chr(ord(a[i]) ^ ord(b[i])) for i in range(len(a))])
    elif type(a) is str and not (type(b) is str):
        b = struct.pack("L", b)
        return xor(a, b)
    else:
        return a ^ b


def rol32(a, b):
    return (a << (b % 32)) | (a >> (32 - (b % 32))) & 0xff


def ror32(a, b):
    return (a >> (b % 32)) | (a << (32 - (b % 32))) & 0xff


def entropy(data):
    if not data:
        return 0
    entropy = 0
    for x in range(256):
        p_x = float(data.count(chr(x))) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy


def read(stream, size, offset=0, littleendian=True):
    typesize = {'L': 4, 'H': 2, 'B': 1, 'Q': 8}
    if littleendian:
        return struct.unpack('<' + size, stream[offset:offset + typesize[size]].tobytes())[0]
    else:
        return struct.unpack(size, stream[offset:offset + typesize[size]].tobytes())[0]


def readArray(stream, size, count, offset=0, littleendian=True):
    typesize = {'L': 4, 'H': 2, 'B': 1, 'Q': 8}
    a = []
    for i in range(count):
        if littleendian:
            a.append(struct.unpack('<' + size,
                                   stream[offset + typesize[size] * i:offset + typesize[size] * (i + 1)].tobytes())[0])
        else:
            a.append(
                struct.unpack(size, stream[offset + typesize[size] * i:offset + typesize[size] * (i + 1)].tobytes())[0])
    return a


def download(url, filename):
    u = urllib2.urlopen(url)
    f = open(filename, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    sys.stdout.write("[-] Progress: |")
    bar = "/\\"
    file_size_dl = 0
    block_sz = file_size / 50
    ibar = 0
    while True:
        tmp_buffer = u.read(block_sz)
        if not tmp_buffer:
            break
        file_size_dl += len(tmp_buffer)
        f.write(tmp_buffer)
        sys.stdout.write(bar[ibar % 2])
        ibar += 1
    f.close()
    sys.stdout.write("|\n")
