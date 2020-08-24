from ctypes import *

(UNKNOWN, WINDOWS, LINUX, MAC) = (0, 1, 2, 3)

INT3 = "\xCC"

HANDLE = c_void_p
LPVOID = c_void_p
DWORD = c_ulong
WORD = c_ushort
CHAR = c_char
ULONG = c_ulong
LONG = c_long
LPSTR = c_void_p
LPCSTR = c_void_p
BYTE = c_char
LPBYTE = POINTER(BYTE)
BOOL = c_int

LPTHREAD_START_ROUTINE = WINFUNCTYPE(DWORD, LPVOID)


#http://msdn.microsoft.com/en-us/library/windows/desktop/ms684873(v=vs.85).aspx
class ProcessInfo(Structure):
    _fields_ = [('hProcess', HANDLE),
                ('hThread', HANDLE),
                ('dwProcessId', DWORD),
                ('dwThreadId', DWORD),
    ]


#http://msdn.microsoft.com/en-us/library/windows/desktop/ms686331(v=vs.85).aspx
class StartupInfo(Structure):
    _fields_ = [('cb', DWORD),
                ('lpReserved', LPSTR),
                ('lpDesktop', LPSTR),
                ('lpTitle', LPSTR),
                ('dwX', DWORD),
                ('dwY', DWORD),
                ('dwXSize', DWORD),
                ('dwYSize', DWORD),
                ('dwXCountChars', DWORD),
                ('dwYCountChars', DWORD),
                ('dwFillAttribute', DWORD),
                ('dwFlags', DWORD),
                ('wShowWindow', WORD),
                ('cbReserved2', WORD),
                ('lpReserved2', LPBYTE),
                ('hStdInput', HANDLE),
                ('hStdOutput', HANDLE),
                ('hStdError', HANDLE),
    ]

#http://msdn.microsoft.com/en-us/library/windows/desktop/aa363082(v=vs.85).aspx
class EXCEPTION_RECORD(Structure):
    pass


EXCEPTION_RECORD._fields_ = [('ExceptionCode', DWORD),
                             ('ExceptionFlags', DWORD),
                             ('ExceptionRecord', POINTER(EXCEPTION_RECORD)),
                             ('ExceptionAddress', LPVOID),
                             ('NumberParameters', DWORD),
                             ('ExceptionInformation', POINTER(ULONG) * 15),
]


#http://msdn.microsoft.com/en-us/library/windows/desktop/ms679326(v=vs.85).aspx
class EXCEPTION_DEBUG_INFO(Structure):
    _fields_ = [('ExceptionRecord', EXCEPTION_RECORD),
                ('dwFirstChance', DWORD),
    ]


#http://msdn.microsoft.com/en-us/library/windows/desktop/ms679287(v=vs.85).aspx
class CREATE_THREAD_DEBUG_INFO(Structure):
    _fields_ = [('hThread', HANDLE),
                ('lpThreadLocalBase', LPVOID),
                ('lpStartAddress', LPTHREAD_START_ROUTINE),
    ]


class CREATE_PROCESS_DEBUG_INFO(Structure):
    _fields_ = [('hFile', HANDLE),
                ('hProcess', HANDLE),
                ('hThread', HANDLE),
                ('dwDebugInfoFileOffset', DWORD),
                ('nDebugInfoSize', DWORD),
                ('lpThreadLocalBase', LPVOID),
                ('lpStartAddress', LPVOID),
                ('lpImageName', LPVOID),
                ('fUnicode', WORD)]


class EXIT_THREAD_DEBUG_INFO(Structure):
    _fields_ = [('dwExitCode', DWORD)]


class EXIT_PROCESS_DEBUG_INFO(Structure):
    _fields_ = [('dwExitCode', DWORD)]


class LOAD_DLL_DEBUG_INFO(Structure):
    _fields_ = [('hFile', HANDLE),
                ('lpBaseOfDll', LPVOID),
                ('dwDebugInfoFileOffset', DWORD),
                ('nDebugInfoSize', DWORD),
                ('lpImageName', LPVOID),
                ('fUnicode', WORD)]


class UNLOAD_DLL_DEBUG_INFO(Structure):
    _fields_ = [('lpBaseOfDll', LPVOID)]


class OUTPUT_DEBUG_STRING_INFO(Structure):
    _fields_ = [('lpDebugStringData', LPSTR),
                ('fUnicode', WORD),
                ('nDebugStringLength', WORD)]


class RIP_INFO(Structure):
    _fields_ = [('dwError', DWORD),
                ('dwType', DWORD)]


class POSSIBLE_DEBUG_EVENT(Union):
    _fields_ = [('Exception', EXCEPTION_DEBUG_INFO),
                ('CreateThread', CREATE_THREAD_DEBUG_INFO),
                ('CreateProcessInfo', CREATE_PROCESS_DEBUG_INFO),
                ('ExitThread', EXIT_THREAD_DEBUG_INFO),
                ('ExitProcess', EXIT_PROCESS_DEBUG_INFO),
                ('LoadDll', LOAD_DLL_DEBUG_INFO),
                ('UnloadDll', UNLOAD_DLL_DEBUG_INFO),
                ('DebugString', OUTPUT_DEBUG_STRING_INFO),
                ('RipInfo', RIP_INFO)
    ]


#http://msdn.microsoft.com/en-us/library/windows/desktop/ms679308(v=vs.85).aspx
class DEBUG_EVENT(Structure):
    _fields_ = [('dwDebugEventCode', DWORD),
                ('dwProcessId', DWORD),
                ('dwThreadId', DWORD),
                ('u', POSSIBLE_DEBUG_EVENT)
    ]


class LUID(Structure):
    _fields_ = [
        # C:/PROGRA~1/gccxml/bin/Vc6/Include/winnt.h 394
        ('LowPart', DWORD),
        ('HighPart', LONG),
    ]


class LUID_AND_ATTRIBUTES(Structure):
    _fields_ = [
        # C:/PROGRA~1/gccxml/bin/Vc6/Include/winnt.h 3241
        ('Luid', LUID),
        ('Attributes', DWORD),
    ]


class TOKEN_PRIVILEGES(Structure):
    _fields_ = [
        # C:/PROGRA~1/gccxml/bin/Vc6/Include/winnt.h 4188
        ('PrivilegeCount', DWORD),
        ('Privileges', LUID_AND_ATTRIBUTES * 1),
    ]

class TOKEN_PRIVS(Structure):
    _fields_ = (
        ("PrivilegeCount",    ULONG),
        ("Privileges",        ULONG * 3 )
    )

SCS_32BIT_BINARY = 0 # A 32-bit Windows-based application
SCS_64BIT_BINARY = 6 # A 64-bit Windows-based application
SCS_DOS_BINARY = 1 # An MS-DOS-based application
SCS_OS216_BINARY = 5 # A 16-bit OS/2-based application
SCS_PIF_BINARY = 3 # A PIF file that executes an MS-DOS-based application
SCS_POSIX_BINARY = 4 # A POSIX-based application
SCS_WOW_BINARY = 2 # A 16-bit Windows-based application

###
### manually declare various #define's as needed.
###

# debug event codes.
EXCEPTION_DEBUG_EVENT = 0x00000001
CREATE_THREAD_DEBUG_EVENT = 0x00000002
CREATE_PROCESS_DEBUG_EVENT = 0x00000003
EXIT_THREAD_DEBUG_EVENT = 0x00000004
EXIT_PROCESS_DEBUG_EVENT = 0x00000005
LOAD_DLL_DEBUG_EVENT = 0x00000006
UNLOAD_DLL_DEBUG_EVENT = 0x00000007
OUTPUT_DEBUG_STRING_EVENT = 0x00000008
RIP_EVENT = 0x00000009
USER_CALLBACK_DEBUG_EVENT = 0xDEADBEEF  # added for callback support in debug event loop.

# debug exception codes.
#http://msdn.microsoft.com/en-us/library/windows/desktop/aa363082(v=vs.85).aspx
#codes number in http://svn.netlabs.org/repos/odin32/trunk/include/exceptions.h 
EXCEPTION_ACCESS_VIOLATION = 0xC0000005
EXCEPTION_ARRAY_BOUNDS_EXCEEDED = 0xC000008C
EXCEPTION_BREAKPOINT = 0x80000003
EXCEPTION_WX86_BREAKPOINT = 0x4000001f
EXCEPTION_DATATYPE_MISALIGNMENT = 0x80000002
#EXCEPTION_FLT_DIVIDE_BY_ZERO   = 0xC000008e
#EXCEPTION_FLT_INVALID_OPERATION= 0xC0000090
#EXCEPTION_FLT_OVERFLOW         = 0xC0000091
#EXCEPTION_FLT_STACK_CHECK      = 0xC0000092
EXCEPTION_ILLEGAL_INSTRUCTION = 0xC000001d
EXCEPTION_IN_PAGE_ERROR = 0xC0000006
#EXCEPTION_INT_DIVIDE_BY_ZERO   = 0xC0000094                 
#EXCEPTION_INT_OVERFLOW         = 0xC0000095
EXCEPTION_NONCONTINUABLE_EXCEPTION = 0xC0000025
EXCEPTION_PRIV_INSTRUCTION = 0xC0000096
#EXCEPTION_SINGLE_STEP          = 0x80000004
EXCEPTION_STACK_OVERFLOW = 0xC00000FD

# hw breakpoint conditions
HW_ACCESS = 0x00000003
HW_EXECUTE = 0x00000000
HW_WRITE = 0x00000001

CONTEXT_CONTROL = 0x00010001
CONTEXT_FULL = 0x00010007
CONTEXT_DEBUG_REGISTERS = 0x00010010
CREATE_NEW_CONSOLE = 0x00000010
DBG_CONTINUE = 0x00010002
DBG_EXCEPTION_NOT_HANDLED = 0x80010001
DBG_EXCEPTION_HANDLED = 0x00010001
DEBUG_PROCESS = 0x00000001
DEBUG_ONLY_THIS_PROCESS = 0x00000002
EFLAGS_RF = 0x00010000
EFLAGS_TRAP = 0x00000100
ERROR_NO_MORE_FILES = 0x00000012
FILE_MAP_READ = 0x00000004
FORMAT_MESSAGE_ALLOCATE_BUFFER = 0x00000100
FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
INVALID_HANDLE_VALUE = 0xFFFFFFFF
MEM_COMMIT = 0x00001000
MEM_DECOMMIT = 0x00004000
MEM_IMAGE = 0x01000000
MEM_RELEASE = 0x00008000
PAGE_NOACCESS = 0x00000001
PAGE_READONLY = 0x00000002
PAGE_READWRITE = 0x00000004
PAGE_WRITECOPY = 0x00000008
PAGE_EXECUTE = 0x00000010
PAGE_EXECUTE_READ = 0x00000020
PAGE_EXECUTE_READWRITE = 0x00000040
PAGE_EXECUTE_WRITECOPY = 0x00000080
PAGE_GUARD = 0x00000100
PAGE_NOCACHE = 0x00000200
PAGE_WRITECOMBINE = 0x00000400
PROCESS_ALL_ACCESS = 0x001F0FFF
SE_PRIVILEGE_ENABLED = 0x00000002
SW_SHOW = 0x00000005
THREAD_ALL_ACCESS = 0x001F03FF
TOKEN_ADJUST_PRIVILEGES = 0x00000020
TOKEN_QUERY = 0x00000008
UDP_TABLE_OWNER_PID = 0x00000001
VIRTUAL_MEM = 0x00003000

