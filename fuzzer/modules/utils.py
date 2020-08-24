import glob
import hashlib
import os
import sys
from urllib.request import urlopen

import modules.logger


def is_executable(exe):
    if exe == "":
        modules.logger.logWarn("No executable file provided")
        return False
    if not os.path.isfile(exe):
        modules.logger.logWarn("No such file: " + exe)
        return False
    if not os.access(exe, os.X_OK):
        modules.logger.logWarn("The file is not executable. Please check the rights")
        return False
    return True


def sha256(filename):
    h = hashlib.sha256()
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


def download(url, filename):
    u = urlopen(url)
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
