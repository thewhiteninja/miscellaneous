from builtins import str
import os
import sys
import time
import ctypes
import platform

FILE_LIST_DIRECTORY = 0x0001

FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004

CREATE_NEW = 1
CREATE_ALWAYS = 2
OPEN_EXISTING = 3
OPEN_ALWAYS = 4
TRUNCATE_EXISTING = 5

FILE_FLAG_BACKUP_SEMANTICS = 0x02000000

FILE_NOTIFY_CHANGE_FILE_NAME = 0x00000001
FILE_NOTIFY_CHANGE_DIR_NAME = 0x00000002
FILE_NOTIFY_CHANGE_ATTRIBUTES = 0x00000004
FILE_NOTIFY_CHANGE_SIZE = 0x00000008
FILE_NOTIFY_CHANGE_LAST_WRITE = 0x00000010
FILE_NOTIFY_CHANGE_LAST_ACCESS = 0x00000020
FILE_NOTIFY_CHANGE_CREATION = 0x00000040
FILE_NOTIFY_CHANGE_SECURITY = 0x00000100

CHANGES = {
    0x00000001: "added",
    0x00000002: "removed",
    0x00000003: "modified",
    0x00000004: "renamed (Old)",
    0x00000005: "renamed (New)"
}

INVALID_HANDLE_VALUE = -1


class FILE_NOTIFY_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("NextEntryOffset", ctypes.c_ulong),
        ("Action", ctypes.c_ulong),
        ("FileNameLength", ctypes.c_ulong),
        ("FileName", (ctypes.c_wchar * 1))
    ]

def watch(h):
    log("Watching events ...")
    buffer = ctypes.create_unicode_buffer(1024)
    lpBytesReturned = ctypes.c_ulong()
    while True:
        results = ctypes.windll.kernel32.ReadDirectoryChangesW(
            h,
            buffer,
            1024,
            True,
            FILE_NOTIFY_CHANGE_FILE_NAME |
            FILE_NOTIFY_CHANGE_DIR_NAME |
            FILE_NOTIFY_CHANGE_ATTRIBUTES |
            FILE_NOTIFY_CHANGE_SIZE |
            FILE_NOTIFY_CHANGE_LAST_WRITE |
            FILE_NOTIFY_CHANGE_LAST_ACCESS |
            FILE_NOTIFY_CHANGE_CREATION |
            FILE_NOTIFY_CHANGE_SECURITY,
            ctypes.byref(lpBytesReturned),
            None,
            None
        )
        if results == 0:
            log("Error 0x%08x : Unable to read directory changes" % ctypes.GetLastError())
            break
        else:
            toSkip = 0
            while lpBytesReturned.value > 0:
                pEntry = ctypes.cast(ctypes.addressof(buffer) + toSkip, ctypes.POINTER(FILE_NOTIFY_INFORMATION))
                toSkip = pEntry[0].NextEntryOffset
                name = ctypes.wstring_at(ctypes.addressof(pEntry[0]) + FILE_NOTIFY_INFORMATION.FileName.offset, pEntry[0].FileNameLength >> 1)
                log("%s %s : %s" % ("Directory" if os.path.isdir(name) else "File", CHANGES[pEntry[0].Action], name))
                if toSkip == 0:
                    break
                lpBytesReturned.value -= toSkip
                


def open_dir(d):
    log("Opening %s ..." % d)
    hDir = ctypes.windll.kernel32.CreateFileW(
        str(d),
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        None
    )
    return hDir


def log(s):
    print("[+] %s" % s)


def usage():
    print("Usage : " + os.path.basename(sys.argv[0]) + " [path]")
    print()
    sys.exit(1)


def main():
    print("Starting %s at %s (%s version)\n" % (
        os.path.basename(sys.argv[0]), time.asctime(time.localtime(time.time())), platform.architecture()[0]))
    if len(sys.argv) != 2:
        usage()
    else:
        hDir = open_dir(sys.argv[1])
        if hDir == INVALID_HANDLE_VALUE:
            log("Error 0x%08x : Unable to call CreateFile on the specified path" % ctypes.GetLastError())
            exit(1)
        watch(hDir)


if __name__ == "__main__":
    main()
