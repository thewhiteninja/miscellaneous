import platform
import struct
import time

import modules.logger
import modules.utils
from modules.debugger_breakpoints import *
from modules.debugger_modules import *
from modules.debugger_process import *
from modules.defines import *

from modules.defines import WINDOWS


class DebuggerOptions:
    def __init__(self):
        self.debug_only_this_process = True
        self.handle_crashes_only = False
        self.process_timeout = 0

class Debugger:
    def __init__(self):

        # Platform detection
        s = platform.platform()
        if s.startswith("Windows"):
            self.os = WINDOWS
            self.kernel32 = windll.kernel32
        elif s.startswith("Linux"):
            self.os = LINUX
        elif s.startswith("Mac"):
            self.os = MAC
        else:
            self.os = UNKNOWN
        self.is_on_python64 = False
        if platform.architecture()[0] == "64bit":
            self.is_on_python64 = True

        # Information about the executable
        self.executable_type = SCS_32BIT_BINARY
        self.executable_path = ""
        self.arguments = ""
        self.loaded = False

        # Information about the process
        self.process = DebuggerProcess()
        self.modules = DebuggerModules()
        self.breakpoints = DebuggerBreakpoints()

        # Debugger options
        self.options = DebuggerOptions()

    def set_debug_privileges(self):
        token_hande = HANDLE()
        luid = LUID()
        token_state = TOKEN_PRIVILEGES()
        if not windll.advapi32.OpenProcessToken(windll.kernel32.GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, byref(token_hande)):
            modules.logger.logWarn("OpenProcessToken (%d)" % (get_last_error()))
        else:
            if not windll.advapi32.LookupPrivilegeValueA(0, "seDebugPrivilege", byref(luid)):
                modules.logger.logWarn("LookupPrivilegeValue (%d)" % (get_last_error()))
            else:
                token_state.PrivilegeCount = 1
                token_state.Privileges[0].Luid = luid
                token_state.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
                if not windll.advapi32.AdjustTokenPrivileges(token_hande, 0, byref(token_state), 0, 0, 0):
                    modules.logger.logWarn("AdjustTokenPrivileges (%d)" % (get_last_error()))
            windll.kernel32.CloseHandle(token_hande)

    def _dereference(self, address):
        dereferenced_address = 0
        if self.is_on_python64:
            dereferenced_address = struct.unpack("<Q", self.read_process_memory(address, 8))[0]
        else:
            dereferenced_address = struct.unpack("<L", self.read_process_memory(address, 4))[0]
        return dereferenced_address

    def _read_string_pointer(self, address, unicode_encoded, length=256):
        dereferenced_address = self._dereference(address)
        return self._read_string(dereferenced_address, unicode_encoded, length)

    def _read_string(self, address, unicode_encoded, length=256):
        if address != 0:
            if self.is_on_python64:
                data = self.read_process_memory(address, length)
            else:
                data = self.read_process_memory(address, length)
            if unicode_encoded:
                return modules.utils.unicode_to_ansi(data)
            else:
                return data
        return None

    def virtual_protect(self, address, length, protection):
        old_protection = c_ulong(0)
        if self.is_on_python64:
            self.kernel32.VirtualProtectEx.argtypes = [c_int, c_uint64, c_int, c_long, POINTER(c_ulong)]
            p = self.kernel32.VirtualProtectEx(self.process.process_handle, c_uint64(address), length, protection,
                                               byref(old_protection))
        else:
            self.kernel32.VirtualProtectEx.argtypes = [c_int, c_ulong, c_int, c_long, POINTER(c_ulong)]
            p = self.kernel32.VirtualProtectEx(self.process.process_handle, address, length, protection, byref(old_protection))
        if not p:
            modules.logger.logWarn("Unable to VirtualProtectEx [%08x, %d] with protection %08x" % (address, length, protection))
            return 0
        else:
            return old_protection.value

    def read_process_memory(self, address, length):
        data = ""
        read_buf = create_string_buffer(length)
        if self.is_on_python64:
            count = c_int64(0)
        else:
            count = c_ulong(0)
        old_protect = self.virtual_protect(address, length, PAGE_EXECUTE_READWRITE)
        tmp_length = length
        while length:
            if self.is_on_python64:
                self.kernel32.ReadProcessMemory.argtypes = [c_int, c_uint64, c_char_p, c_long, POINTER(c_int64)]
                r = self.kernel32.ReadProcessMemory(self.process.process_handle, c_uint64(address), read_buf, length, byref(count))
            else:
                r = self.kernel32.ReadProcessMemory(self.process.process_handle, address, read_buf, length, byref(count))
            if not r:
                if not len(data):
                    modules.logger.logWarn(
                        "Unable to read %d bytes from address %s (%d)" % (length, hex(address), GetLastError()))
                    break
                else:
                    return data
            data += read_buf.raw
            length -= count.value
            address += count.value
        if old_protect:
            self.virtual_protect(address, tmp_length, old_protect)
        return data

    def write_process_memory(self, address, value):
        if self.is_on_python64:
            count = c_int64(0)
        else:
            count = c_ulong(0)
        old_protect = self.virtual_protect(address, len(value), PAGE_EXECUTE_READWRITE)
        tmp_length = len(value)
        while len(value) > 0:
            if self.is_on_python64:
                self.kernel32.WriteProcessMemory.argtypes = [c_int, c_uint64, c_char_p, c_long, POINTER(c_int64)]
                r = self.kernel32.WriteProcessMemory(self.process.process_handle, c_uint64(address), value, len(value), byref(count))
            else:
                r = self.kernel32.WriteProcessMemory(self.process.process_handle, address, value, len(value), byref(count))
            if not r:
                modules.logger.logWarn("Unable to write %d bytes to address %08x (%d)" % (len(value), address, GetLastError()))
                return False
            value = value[count.value:]
        if old_protect:
            self.virtual_protect(address, tmp_length, old_protect)
        return True

    def terminate(self):
        windll.kernel32.TerminateProcess(self.process.process_handle, 0)
        windll.kernel32.CloseHandle(self.process.process_handle)
        self.process.process_handle = -1
        self.process.pid = -1

    def get_context(self):
        pass

    def set_context(self):
        pass

    def load(self, exe, args):
        if modules.utils.is_executable(exe):
            self.executable_path = exe
            self.arguments = args
            if self.os == WINDOWS:
                binary_type = c_ulong(0)
                self.kernel32.GetBinaryTypeA(c_char_p(self.executable_path), byref(binary_type))
                self.executable_type = binary_type.value
                pi = ProcessInfo()
                si = StartupInfo()
                mode = DEBUG_ONLY_THIS_PROCESS
                if not self.options.debug_only_this_process:
                    mode = DEBUG_PROCESS
                if not self.kernel32.CreateProcessA(c_char_p(0), c_char_p(self.executable_path + " " + self.arguments), 0, 0, False, mode, 0, 0, byref(si), byref(pi)):
                    if not self.is_on_python64 and self.executable_type == SCS_64BIT_BINARY:
                        modules.logger.logErr("Unable create 64bit process using Python 32bit (%d)" % (self.kernel32.GetLastError()))
                    else:
                        modules.logger.logErr("Unable create process: %s (%d)" % (self.executable_path, self.kernel32.GetLastError()))
                    self.loaded = False
                else:
                    self.process.pid = pi.dwProcessId
                    self.process.process_handle = pi.hProcess
                    self.loaded = True
            elif self.os == LINUX:
                modules.logger.logWarn("Debugger(load) is not implemented for linux platform")
            elif self.os == MAC:
                modules.logger.logWarn("Debugger(load) is not implemented for mac platform")
            else:
                modules.logger.logWarn("Debugger(load) is not implemented for your platform")

    def set_breakpoint(self, address, handler, condition=None):
        if self.loaded:
            bp = self.breakpoints.add(address)
            if bp:
                bp.handler = handler
                bp.condition = condition
                bp.backup = self.read_process_memory(bp.address, 1)
                if self.write_process_memory(bp.address, INT3):
                    self.process.dirty_memory = True
                    modules.logger.logInfo("Breakpoint at %08x added"% bp.address)
            else:
                modules.logger.logWarn("Breakpoint at %08x already exists"% address)

    def del_all_breakpoints(self):
        if self.loaded:
            for bp in self.breakpoints.get_all():
                if self.write_process_memory(bp.address, bp.backup):
                    self.process.dirty_memory = True
            self.breakpoints.breakpoints.clear()
            if len(self.breakpoints.get_all()) == 0:
                modules.logger.logInfo("All breakpoint removed")

    def del_breakpoint(self, address):
        if self.loaded:
            bp = self.breakpoints.remove(address)
            if bp:
                if self.write_process_memory(bp.address, bp.backup):
                    self.process.dirty_memory = True
                    modules.logger.logInfo("Breakpoint at %08x removed"% address)
            else:
                modules.logger.logWarn("Breakpoint at %08x already removed"% address)

    def get_all_breakpoints(self):
        return self.breakpoints.get_all()

    def show_breakpoints(self):
        if self.breakpoints.count()==0:
            modules.logger.logInfo("No breakpoints set")
        else:
            i = 0
            modules.logger.logInfo("----------------------------------------")
            modules.logger.logInfo(" bp | address    | handler")
            modules.logger.logInfo("----------------------------------------")
            for bp in self.breakpoints.get_all():
                modules.logger.logInfo("%3d | 0x%08x | %s"%(i, bp.address, bp.handler.__name__ ))
                i += 1
            modules.logger.logInfo("----------------------------------------")

    def run(self):
        if not self.loaded:
            modules.logger.logErr("No executable loaded")
        else:
            if self.os == WINDOWS:
                firstBreakpoint = True
                maxTime = time.time() + self.options.process_timeout
                debug = DEBUG_EVENT()
                while 1:
                    if self.kernel32.WaitForDebugEvent(byref(debug), 100):
                        if debug.dwDebugEventCode == EXCEPTION_DEBUG_EVENT:
                            code = debug.u.Exception.ExceptionRecord.ExceptionCode
                            address = debug.u.Exception.ExceptionRecord.ExceptionAddress
                            if code == EXCEPTION_BREAKPOINT:
                                if firstBreakpoint:
                                    firstBreakpoint = False
                                else:
                                    bp = self.breakpoints.get(address)
                                    if bp:
                                        bp.handler(bp)
                            elif code == EXCEPTION_WX86_BREAKPOINT:
                                modules.logger.logInfo("WOW64 initialized")
                                print(hex(code), hex(address))
                            else:
                                modules.logger.logWarn('Crash: exception code : %08x at %08x' % (
                                    debug.u.Exception.ExceptionRecord.ExceptionCode,
                                    debug.u.Exception.ExceptionRecord.ExceptionAddress))
                                break
                        elif debug.dwDebugEventCode == EXIT_PROCESS_DEBUG_EVENT:
                                modules.logger.logInfo("Process exited with code: 0x%x"% debug.u.ExitProcess.dwExitCode)
                                break
                        elif not self.options.handle_crashes_only:
                            if debug.dwDebugEventCode == CREATE_THREAD_DEBUG_EVENT:
                                modules.logger.logInfo("New thread: %d at %08x"%(debug.u.CreateThread.hThread, debug.u.CreateThread.lpStartAddress))
                            elif debug.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT:
                                modules.logger.logInfo("New process: %d at %08x"%(debug.dwProcessId,debug.u.CreateProcessInfo.lpStartAddress))
                            elif debug.dwDebugEventCode == EXIT_THREAD_DEBUG_EVENT:
                                modules.logger.logInfo("Thread exited with code: 0x%x"% debug.u.ExitThread.dwExitCode)
                            elif debug.dwDebugEventCode == LOAD_DLL_DEBUG_EVENT:
                                mod = self.modules.add(debug.u.LoadDll.lpBaseOfDll)
                                mod.path = self._read_string_pointer(debug.u.LoadDll.lpImageName, debug.u.LoadDll.fUnicode)
                                modules.logger.logInfo("Dll loaded: %s at 0x%08x"%(mod.path,mod.base_address))
                            elif debug.dwDebugEventCode == UNLOAD_DLL_DEBUG_EVENT:
                                self.modules.remove(debug.u.UnloadDll.lpBaseOfDll)
                                modules.logger.logInfo("Dll unloaded: " + hex(debug.u.UnloadDll.lpBaseOfDll))
                            elif debug.dwDebugEventCode == OUTPUT_DEBUG_STRING_EVENT:
                                modules.logger.logInfo("Debug string: %s"%(self._read_string(debug.u.DebugString.lpDebugStringData, debug.u.DebugString.fUnicode, debug.u.DebugString.nDebugStringLength)))
                            elif debug.dwDebugEventCode == RIP_EVENT:
                                modules.logger.logInfo("RIP event not implemented")
                            elif debug.dwDebugEventCode == USER_CALLBACK_DEBUG_EVENT:
                                modules.logger.logInfo("USER_CALLBACK event not implemented")
                            else:
                                modules.logger.logErr("Debug event not implemented")
                    if maxTime < time.time():
                        break

                    if self.process.dirty_memory:
                        self.kernel32.FlushInstructionCache(self.process.process_handle, 0, 0)
                        self.process.dirty_memory = False
                    self.kernel32.ContinueDebugEvent(debug.dwProcessId, debug.dwThreadId, DBG_CONTINUE)
                self.terminate()
            elif self.os == LINUX:
                modules.logger.logWarn("Debugger(run) is not implemented for linux platform")
            elif self.os == MAC:
                modules.logger.logWarn("Debugger(run) is not implemented for mac platform")
            else:
                modules.logger.logWarn("Debugger(run) is not implemented for your platform")
