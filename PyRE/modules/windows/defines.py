from ctypes import *

(UNKNOWN, WINDOWS, LINUX, MAC) = (0, 1, 2, 3)
INFINITE = 0xffffffff

INT3 = "\xCC"

HANDLE = c_void_p
LPVOID = c_void_p
DWORD = c_ulong
DWORD64 = c_uint64
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

CONTEXT_x86 = 0x00010000
CONTEXT_AMD_64 = 0x00100000


# Which parts of the Context struct to show
CONTEXT_CONTROL = 0x1
CONTEXT_INTEGER = 0x2
CONTEXT_SEGMENTS = 0x4
CONTEXT_FLOATING_POINT = 0x8
CONTEXT_DEBUG_REGISTERS = 0x10

CONTEXT_FULL_64 = (CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_FLOATING_POINT)
CONTEXT_ALL_64 = (CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_SEGMENTS | CONTEXT_FLOATING_POINT |
                  CONTEXT_DEBUG_REGISTERS)


# x86/WOW64-specific
CONTEXT_XSTATE_32 = 0x40
CONTEXT_EXTENDED_REGISTERS = 0x20

CONTEXT_FULL_32 = (CONTEXT_CONTROL | CONTEXT_INTEGER |
                   CONTEXT_SEGMENTS)

CONTEXT_ALL_32 = (CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_SEGMENTS |
                  CONTEXT_FLOATING_POINT | CONTEXT_DEBUG_REGISTERS |
                  CONTEXT_EXTENDED_REGISTERS)

# AMD_64-specific
CONTEXT_XSTATE_64 = 0x20
CONTEXT_EXCEPTION_ACTIVE = 0x8000000
CONTEXT_SERVICE_ACTIVE = 0x10000000
CONTEXT_EXCEPTION_REQUEST = 0x40000000
CONTEXT_EXCEPTION_REPORTING = 0x80000000

IMAGE_FILE_MACHINE_AMD64 = 0x8664
IMAGE_FILE_MACHINE_I386 = 0x14C

# characteristics
IMAGE_FILE_LARGE_ADDRESS_AWARE = 0x0020
IMAGE_FILE_32BIT_MACHINE = 0x0100
IMAGE_FILE_DEBUG_STRIPPED = 0x0200
IMAGE_FILE_REMOVABLE_RUN_FROM_SWAP = 0x0400
IMAGE_FILE_NET_RUN_FROM_SWAP = 0x0800
IMAGE_FILE_SYSTEM = 0x1000
IMAGE_FILE_DLL = 0x2000
IMAGE_FILE_UP_SYSTEM_ONLY = 0x4000  # uniprocessor only

# section characteristics

IMAGE_SCN_CNT_CODE = 0x00000020
IMAGE_SCN_CNT_INITIALIZED_DATA = 0x00000040
IMAGE_SCN_CNT_UNINITIALIZED_DATA = 0x00000080
IMAGE_SCN_LNK_INFO = 0x00000200
IMAGE_SCN_LNK_REMOVE = 0x00000800
IMAGE_SCN_ALIGN_1BYTES = 0x00100000
IMAGE_SCN_ALIGN_2BYTES = 0x00200000
IMAGE_SCN_ALIGN_4BYTES = 0x00300000
IMAGE_SCN_ALIGN_8BYTES = 0x00400000
IMAGE_SCN_ALIGN_16BYTES = 0x00500000
IMAGE_SCN_ALIGN_32BYTES = 0x00600000
# ... until 8192 bytes.
IMAGE_SCN_ALIGN_8192BYTES = 0x00E00000
IMAGE_SCN_LNK_NRELOC_OVFL = 0x01000000
IMAGE_SCN_MEM_DISCARDABLE = 0x02000000
IMAGE_SCN_MEM_NOT_CACHED = 0x04000000
IMAGE_SCN_MEM_NOT_PAGED = 0x08000000
IMAGE_SCN_MEM_SHARED = 0x10000000
IMAGE_SCN_MEM_EXECUTE = 0x20000000
IMAGE_SCN_MEM_READ = 0x40000000
IMAGE_SCN_MEM_WRITE = 0x80000000

# relocation type
IMAGE_REL_I386_ABSOLUTE = 0x0000
IMAGE_REL_I386_DIR32 = 0x0006
IMAGE_REL_I386_DIR32NB = 0x0007
IMAGE_REL_I386_REL32 = 0x0014

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms684873(v=vs.85).aspx


class ProcessInfo(Structure):
    _fields_ = [('hProcess', HANDLE),
                ('hThread', HANDLE),
                ('dwProcessId', DWORD),
                ('dwThreadId', DWORD),
                ]


# http://msdn.microsoft.com/en-us/library/windows/desktop/ms686331(v=vs.85).aspx
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


# http://msdn.microsoft.com/en-us/library/windows/desktop/aa363082(v=vs.85).aspx
class EXCEPTION_RECORD(Structure):
    pass


EXCEPTION_RECORD._fields_ = [('ExceptionCode', DWORD),
                             ('ExceptionFlags', DWORD),
                             ('ExceptionRecord', POINTER(EXCEPTION_RECORD)),
                             ('ExceptionAddress', LPVOID),
                             ('NumberParameters', DWORD),
                             ('ExceptionInformation', POINTER(ULONG) * 15),
                             ]


# http://msdn.microsoft.com/en-us/library/windows/desktop/ms679326(v=vs.85).aspx
class EXCEPTION_DEBUG_INFO(Structure):
    _fields_ = [('ExceptionRecord', EXCEPTION_RECORD),
                ('dwFirstChance', DWORD),
                ]


# http://msdn.microsoft.com/en-us/library/windows/desktop/ms679287(v=vs.85).aspx
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


# http://msdn.microsoft.com/en-us/library/windows/desktop/ms679308(v=vs.85).aspx
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
        ("PrivilegeCount", ULONG),
        ("Privileges", ULONG * 3)
    )


class FLOATING_SAVE_AREA(Structure):
    _fields_ = [

        ("ControlWord", DWORD),
        ("StatusWord", DWORD),
        ("TagWord", DWORD),
        ("ErrorOffset", DWORD),
        ("ErrorSelector", DWORD),
        ("DataOffset", DWORD),
        ("DataSelector", DWORD),
        ("RegisterArea", BYTE * 80),
        ("Cr0NpxState", DWORD),
    ]


# The CONTEXT structure which holds all of the
# register values after a GetThreadContext() call
# THIS IS THE 32-bit version of the struct. The 64-bit version is below
# See winNT.h.
class CONTEXT(Structure):
    _fields_ = [

        ("ContextFlags", DWORD),
        ("Dr0", DWORD),
        ("Dr1", DWORD),
        ("Dr2", DWORD),
        ("Dr3", DWORD),
        ("Dr6", DWORD),
        ("Dr7", DWORD),
        ("FloatSave", FLOATING_SAVE_AREA),
        ("SegGs", DWORD),
        ("SegFs", DWORD),
        ("SegEs", DWORD),
        ("SegDs", DWORD),
        ("Edi", DWORD),
        ("Esi", DWORD),
        ("Ebx", DWORD),
        ("Edx", DWORD),
        ("Ecx", DWORD),
        ("Eax", DWORD),
        ("Ebp", DWORD),
        ("Eip", DWORD),
        ("SegCs", DWORD),
        ("EFlags", DWORD),
        ("Esp", DWORD),
        ("SegSs", DWORD),
        ("ExtendedRegisters", BYTE * 512),
    ]


class M128A(Structure):
    _fields_ = [
        ("High", DWORD64),
        ("Low", DWORD64)
    ]


#
class XMM_SAVE_AREA32(Structure):
    _fields_ = [
        ("ControlWord", WORD),
        ("StatusWord", WORD),
        ("TagWord", BYTE),
        ("Reserved1", BYTE),
        ("ErrorOpcode", WORD),
        ("ErrorOffset", DWORD),
        ("ErrorSelector", WORD),
        ("Reserved2", WORD),
        ("DataOffset", DWORD),
        ("DataSelector", WORD),
        ("Reserved3", WORD),
        ("MxCsr", DWORD),
        ("MxCsr_Mask", DWORD),
        ("FloatRegisters", M128A * 8)
    ]


# Alternative
class XMM_SAVE_AREA_STRUCT(Structure):
    _fields_ = [
        ("Header", M128A * 2),
        ("Legacy", M128A * 8),
        ("Xmm0", M128A),
        ("Xmm1", M128A),
        ("Xmm2", M128A),
        ("Xmm3", M128A),
        ("Xmm4", M128A),
        ("Xmm5", M128A),
        ("Xmm6", M128A),
        ("Xmm7", M128A),
        ("Xmm8", M128A),
        ("Xmm9", M128A),
        ("Xmm10", M128A),
        ("Xmm11", M128A),
        ("Xmm12", M128A),
        ("Xmm13", M128A),
        ("Xmm14", M128A),
        ("Xmm15", M128A),
    ]


# Union representing the two ways of representing floating-point register state
class FLOAT_UNION(Union):
    _fields_ = [
        ("FltSave", XMM_SAVE_AREA32),
        ("DUMMYSTRUCTNAME", XMM_SAVE_AREA_STRUCT)
    ]


class CONTEXT_AMD64(Structure):
    _fields_ = [
        # Convenience fields

        ("P1Home", DWORD64),
        ("P2Home", DWORD64),
        ("P3Home", DWORD64),
        ("P4Home", DWORD64),
        ("P5Home", DWORD64),
        ("P6Home", DWORD64),

        # Control flags. These are set to indicate to GetThreadContext what
        # should be filled
        ("ContextFlags", DWORD),
        ("MxCsr", DWORD),

        # Segment registers and flags

        ("SegCs", WORD),
        ("SegDs", WORD),
        ("SegEs", WORD),
        ("SegFs", WORD),
        ("SegGs", WORD),
        ("SegSs", WORD),
        ("EFlags", DWORD),

        # Debug registers
        ("Dr0", DWORD64),
        ("Dr1", DWORD64),
        ("Dr2", DWORD64),
        ("Dr3", DWORD64),
        ("Dr6", DWORD64),
        ("Dr7", DWORD64),

        # Integer registers

        ("Rax", DWORD64),
        ("Rcx", DWORD64),
        ("Rdx", DWORD64),
        ("Rbx", DWORD64),
        ("Rsp", DWORD64),
        ("Rbp", DWORD64),
        ("Rsi", DWORD64),
        ("Rdi", DWORD64),
        ("R8;", DWORD64),
        ("R9;", DWORD64),
        ("R10", DWORD64),
        ("R11", DWORD64),
        ("R12", DWORD64),
        ("R13", DWORD64),
        ("R14", DWORD64),
        ("R15", DWORD64),

        # Instruction pointer
        ("Rip", DWORD64),

        # Floating point state
        ("DUMMYUNIONNAME", FLOAT_UNION),

        # Vector registers
        ("VectorRegister", M128A * 27),
        ("VectorControl", DWORD64),

        # Special Debug Control registers

        ("DebugControl", DWORD64),
        ("LastBranchToRip", DWORD64),
        ("LastBranchFromRip", DWORD64),
        ("LastExceptionToRip", DWORD64),
        ("LastExceptionFromRip", DWORD64),
    ]


SCS_32BIT_BINARY = 0  # A 32-bit Windows-based application
SCS_64BIT_BINARY = 6  # A 64-bit Windows-based application
SCS_DOS_BINARY = 1  # An MS-DOS-based application
SCS_OS216_BINARY = 5  # A 16-bit OS/2-based application
SCS_PIF_BINARY = 3  # A PIF file that executes an MS-DOS-based application
SCS_POSIX_BINARY = 4  # A POSIX-based application
SCS_WOW_BINARY = 2  # A 16-bit Windows-based application

###
# manually declare various #define's as needed.
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
# added for callback support in debug event loop.
USER_CALLBACK_DEBUG_EVENT = 0xDEADBEEF

# debug exception codes.
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa363082(v=vs.85).aspx
# codes number in
# http://svn.netlabs.org/repos/odin32/trunk/include/exceptions.h
EXCEPTION_ACCESS_VIOLATION = 0xC0000005
EXCEPTION_ARRAY_BOUNDS_EXCEEDED = 0xC000008C
EXCEPTION_BREAKPOINT = 0x80000003
EXCEPTION_WX86_BREAKPOINT = 0x4000001f
EXCEPTION_DATATYPE_MISALIGNMENT = 0x80000002
# EXCEPTION_FLT_DIVIDE_BY_ZERO   = 0xC000008e
# EXCEPTION_FLT_INVALID_OPERATION= 0xC0000090
# EXCEPTION_FLT_OVERFLOW         = 0xC0000091
# EXCEPTION_FLT_STACK_CHECK      = 0xC0000092
EXCEPTION_ILLEGAL_INSTRUCTION = 0xC000001d
EXCEPTION_IN_PAGE_ERROR = 0xC0000006
# EXCEPTION_INT_DIVIDE_BY_ZERO   = 0xC0000094
# EXCEPTION_INT_OVERFLOW         = 0xC0000095
EXCEPTION_NONCONTINUABLE_EXCEPTION = 0xC0000025
EXCEPTION_PRIV_INSTRUCTION = 0xC0000096
# EXCEPTION_SINGLE_STEP          = 0x80000004
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
