from modules import utils
from debugger_process import *
from debugger_modules import *
from debugger_breakpoints import *
from modules.windows.PE import *


class DebuggerOptions:

    def __init__(self):
        self.debug_only_this_process = True
        self.process_timeout = INFINITE


class Debugger:

    def __init__(self):
        # Information about the system
        self.os32 = not utils.is_OS_64()
        self.python32 = not utils.is_Python_64()

        # Information about the executable
        self.executable_type = SCS_32BIT_BINARY
        self.executable = None
        self.executable_path = ""
        self.arguments = ""
        self.loaded = False
        self.running = False

        # Information about the process
        self.process = DebuggerProcess()
        self.modules = DebuggerModules()
        self.breakpoints = DebuggerBreakpoints()

        # Continue
        self.__threadID = 0
        self.__processID = 0
        self.context = None

        # Debugger options
        self.options = DebuggerOptions()

        self.set_debug_privileges()

    def set_debug_privileges(self):
        token_hande = HANDLE()
        luid = LUID()
        token_state = TOKEN_PRIVILEGES()
        if not windll.advapi32.OpenProcessToken(windll.kernel32.GetCurrentProcess(),
                                                TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, byref(token_hande)):
            logger.logWarn("OpenProcessToken (%d)" % (get_last_error()))
        else:
            if not windll.advapi32.LookupPrivilegeValueA(0, "seDebugPrivilege", byref(luid)):
                logger.logWarn("LookupPrivilegeValue (%d)" %
                               (get_last_error()))
            else:
                token_state.PrivilegeCount = 1
                token_state.Privileges[0].Luid = luid
                token_state.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
                if not windll.advapi32.AdjustTokenPrivileges(token_hande, 0, byref(token_state), 0, 0, 0):
                    logger.logWarn("AdjustTokenPrivileges (%d)" %
                                   (get_last_error()))
            windll.kernel32.CloseHandle(token_hande)

    def _dereference(self, address):
        if self.python32:
            return struct.unpack("<L", self.read_process_memory(address, 4))[0]
        else:
            return struct.unpack("<Q", self.read_process_memory(address, 8))[0]

    def _read_string_pointer(self, address, unicode_encoded, length=256):
        return self._read_string(self._dereference(address), unicode_encoded, length)

    def _read_string(self, address, unicode_encoded, length=256):
        if address != 0:
            data = self.read_process_memory(address, length)
            if unicode_encoded:
                return utils.unicode_to_ansi(data)
            else:
                return data
        return None

    def virtual_protect(self, address, length, protection):
        old_protection = c_ulong(0)
        if self.python32:
            windll.kernel32.VirtualProtectEx.argtypes = [
                c_int, c_ulong, c_int, c_long, POINTER(c_ulong)]
            p = windll.kernel32.VirtualProtectEx(self.process.info.hProcess, address, length, protection,
                                                 byref(old_protection))
        else:
            windll.kernel32.VirtualProtectEx.argtypes = [
                c_int, c_uint64, c_int, c_long, POINTER(c_ulong)]
            p = windll.kernel32.VirtualProtectEx(self.process.info.hProcess, c_uint64(address), length,
                                                 protection,
                                                 byref(old_protection))
        if not p:
            logger.logDebug("Unable to VirtualProtectEx [0x%08x, %d] with protection 0x%08x" % (address, length,
                                                                                                protection))
            return 0
        else:
            return old_protection.value

    def read_process_memory(self, address, length):
        data = ""
        read_buf = create_string_buffer(length)
        if self.python32:
            count = c_ulong(0)
        else:
            count = c_int64(0)
        old_protect = self.virtual_protect(
            address, length, PAGE_EXECUTE_READWRITE)
        tmp_length = length
        while length:
            if self.python32:
                r = windll.kernel32.ReadProcessMemory(self.process.info.hProcess, address, read_buf, length,
                                                      byref(count))
            else:
                windll.kernel32.ReadProcessMemory.argtypes = [
                    c_int, c_uint64, c_char_p, c_long, POINTER(c_int64)]
                r = windll.kernel32.ReadProcessMemory(self.process.info.hProcess, c_uint64(address), read_buf, length,
                                                      byref(count))
            if not r:
                if not len(data):
                    logger.logDebug(
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
        if self.python32:
            count = c_ulong(0)
        else:
            count = c_int64(0)
        old_protect = self.virtual_protect(
            address, len(value), PAGE_EXECUTE_READWRITE)
        tmp_length = len(value)
        while len(value) > 0:
            if self.python32:
                r = windll.kernel32.WriteProcessMemory(self.process.info.hProcess, address, value, len(value),
                                                       byref(count))
            else:
                windll.kernel32.WriteProcessMemory.argtypes = [
                    c_int, c_uint64, c_char_p, c_long, POINTER(c_int64)]
                r = windll.kernel32.WriteProcessMemory(self.process.info.hProcess, c_uint64(address), value, len(value),
                                                       byref(count))
            if not r:
                logger.logWarn("Unable to write %d bytes to address 0x%08x (%d)" % (len(value), address,
                                                                                    GetLastError()))
                return False
            value = value[count.value:]
        if old_protect:
            self.virtual_protect(address, tmp_length, old_protect)
        return True

    def terminate(self):
        if self.process.info.hProcess != -1:
            windll.kernel32.TerminateProcess(self.process.info.hProcess, 0)
            windll.kernel32.CloseHandle(self.process.info.hProcess)
            logger.logInfo("Process killed (PID=%d)" %
                           self.process.info.dwProcessId)
        self.process = DebuggerProcess()
        self.executable = None
        self.loaded = False
        self.running = False

    def get_context(self):
        context = CONTEXT()
        context.ContextFlags = CONTEXT_ALL_32

        if not windll.kernel32.GetThreadContext(self.process.info.hThread, byref(context)):
            logger.logWarn("Unable to get context for thread handle %d (%d)" % (self.process.info.hThread,
                                                                                windll.kernel32.GetLastError()))

        return context

    def set_context(self):
        pass

    def load(self, exe, args):
        if utils.is_executable(exe):
            self.executable_path = exe
            self.arguments = args
            os_type = utils.get_OS()
            if os_type == WINDOWS:
                self.executable_type = utils.get_executable_type(exe)
                logger.logInfo("Loading %s binary on windows %s platform" % (
                    "64bits" if self.executable_type == SCS_64BIT_BINARY else
                    "32bits", "32bits" if self.os32 else
                    "64bits"))
                self.executable = PE(exe)
                pi = ProcessInfo()
                si = StartupInfo()
                mode = DEBUG_ONLY_THIS_PROCESS
                if not self.options.debug_only_this_process:
                    mode = DEBUG_PROCESS
                if not windll.kernel32.CreateProcessA(c_char_p(self.executable_path + " " + self.arguments),
                                                      c_char_p(0),
                                                      0, 0, False, mode, 0, 0, byref(si), byref(pi)):
                    if self.python32 and self.executable_type == SCS_64BIT_BINARY:
                        logger.logErr(
                            "Unable create 64bit process using Python 32bit (%d)" % (windll.kernel32.GetLastError()))
                    else:
                        logger.logErr(
                            "Unable create process: %s (%d)" % (self.executable_path, windll.kernel32.GetLastError()))
                    self.loaded = False
                    self.running = False
                else:
                    self.process.info = pi
                    self.loaded = True
                    self.running = True
                    logger.logInfo(
                        "Process created suspended (PID=%d)" % pi.dwProcessId)
            elif os_type == LINUX:
                logger.logWarn(
                    "Debugger(load) is not implemented for linux platform")
            elif os_type == MAC:
                logger.logWarn(
                    "Debugger(load) is not implemented for mac platform")
            else:
                logger.logWarn(
                    "Debugger(load) is not implemented for your platform")

    def set_breakpoint(self, address, handler=None, condition=None):
        self.set_sw_breakpoint(address, handler, condition=None)

    def set_sw_breakpoint(self, address, handler=None, condition=None):
        if self.loaded:
            bp = self.breakpoints.add(address, handler, condition)
            if bp:
                bp.backup = self.read_process_memory(bp.address, 1)
                if self.write_process_memory(bp.address, INT3):
                    self.process.dirty_memory = True
                    logger.logInfo("Breakpoint at 0x%08x added" % bp.address)
            else:
                logger.logWarn("Breakpoint at 0x%08x already exists" % address)

    def del_all_breakpoints(self):
        if self.loaded:
            for bp in self.breakpoints.remove_all():
                self.del_breakpoint(bp.address)
            if self.breakpoints.count() == 0:
                logger.logInfo("All breakpoints removed")

    def del_breakpoint(self, address):
        if self.loaded:
            bp = self.breakpoints.remove(address)
            if bp:
                if self.write_process_memory(bp.address, bp.backup):
                    self.process.dirty_memory = True
                    logger.logInfo("Breakpoint at 0x%08x removed" % address)
            else:
                logger.logWarn("No such breakpoint at 0x%08x" % address)

    def __flushInstrCache(self):
        if self.process.dirty_memory:
            windll.kernel32.FlushInstructionCache(
                self.process.info.hProcess, 0, 0)
            self.process.dirty_memory = False

    def resume(self):
        if self.loaded and not self.running:
            if self.process.dirty_memory:
                windll.kernel32.FlushInstructionCache(
                    self.process.info.hProcess, 0, 0)
                self.process.dirty_memory = False
            self.running = True
            windll.kernel32.ContinueDebugEvent(
                self.__processID, self.__threadID, DBG_CONTINUE)
        self.run(True)

    def run(self, resume=False):
        if not self.loaded:
            logger.logErr("No executable loaded")
        else:
            os_type = utils.get_OS()
            if os_type == WINDOWS:
                oint = not resume
                maxTime = time.time() + self.options.process_timeout
                debug = DEBUG_EVENT()
                while 1:
                    self.__flushInstrCache()
                    if windll.kernel32.WaitForDebugEvent(byref(debug), 100):
                        if debug.dwDebugEventCode == EXCEPTION_DEBUG_EVENT:
                            code = debug.u.Exception.ExceptionRecord.ExceptionCode
                            address = debug.u.Exception.ExceptionRecord.ExceptionAddress
                            if code == EXCEPTION_BREAKPOINT:
                                if firstBreakpoint:
                                    firstBreakpoint = False
                                else:
                                    bp = self.breakpoints.get(address)
                                    if bp and bp.handler:
                                        bp.handler(bp)
                                    else:
                                        self.running = False
                                        self.__processID = debug.dwProcessId
                                        self.__threadID = debug.dwThreadId
                                        self.write_process_memory(
                                            bp.address, bp.backup)
                                        windll.kernel32.FlushInstructionCache(
                                            self.process.info.hProcess, 0, 0)
                                        self.context = self.get_context()
                                        logger.logInfo(
                                            "Breakpoint at %08x" % bp.address)
                                        return
                            elif code == EXCEPTION_WX86_BREAKPOINT:
                                logger.logInfo("WOW64 initialized")
                                print hex(code), hex(address)
                            else:
                                logger.logWarn('Crash: exception code : %08x at %08x' % (
                                    debug.u.Exception.ExceptionRecord.ExceptionCode,
                                    debug.u.Exception.ExceptionRecord.ExceptionAddress))
                                self.running = False
                                self.__processID = debug.dwProcessId
                                self.__threadID = debug.dwThreadId
                                return
                        elif debug.dwDebugEventCode == EXIT_PROCESS_DEBUG_EVENT:
                            logger.logInfo(
                                "Process exited with code: 0x%x" % debug.u.ExitProcess.dwExitCode)
                            break
                        elif debug.dwDebugEventCode == CREATE_THREAD_DEBUG_EVENT:
                            logger.logInfo("New thread: Handle %d at starting %08x" % (debug.u.CreateThread.hThread,
                                                                                       debug.u.CreateThread.lpStartAddress))
                        elif debug.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT:
                            logger.logInfo("New process: PID %d loaded at %08x" % (debug.dwProcessId,
                                                                                   debug.u.CreateProcessInfo.lpStartAddress))
                        elif debug.dwDebugEventCode == EXIT_THREAD_DEBUG_EVENT:
                            logger.logInfo("Thread exited with code: 0x%x" %
                                           debug.u.ExitThread.dwExitCode)
                        elif debug.dwDebugEventCode == LOAD_DLL_DEBUG_EVENT:
                            mod = self.modules.add(debug.u.LoadDll.lpBaseOfDll)
                            try:
                                mod.path = self._read_string_pointer(debug.u.LoadDll.lpImageName,
                                                                     debug.u.LoadDll.fUnicode)
                            except:
                                mod.path = "ntdll.dll"
                            logger.logInfo("Dll loaded: %s at 0x%08x" %
                                           (mod.path, mod.base_address))
                        elif debug.dwDebugEventCode == UNLOAD_DLL_DEBUG_EVENT:
                            if self.modules.get_by_base(debug.u.UnloadDll.lpBaseOfDll) is not None:
                                self.modules.remove(
                                    debug.u.UnloadDll.lpBaseOfDll)
                                logger.logInfo(
                                    "Dll unloaded: " + hex(debug.u.UnloadDll.lpBaseOfDll))
                        elif debug.dwDebugEventCode == OUTPUT_DEBUG_STRING_EVENT:
                            logger.logWarn("Debug string: %s" % (self._read_string(
                                debug.u.DebugString.lpDebugStringData, debug.u.DebugString.fUnicode,
                                debug.u.DebugString.nDebugStringLength)))
                        elif debug.dwDebugEventCode == RIP_EVENT:
                            logger.logInfo("RIP event not implemented")
                        elif debug.dwDebugEventCode == USER_CALLBACK_DEBUG_EVENT:
                            logger.logInfo(
                                "USER_CALLBACK event not implemented")
                        else:
                            logger.logErr("Debug event not implemented")
                    if maxTime < time.time():
                        break
                    windll.kernel32.ContinueDebugEvent(
                        debug.dwProcessId, debug.dwThreadId, DBG_CONTINUE)
                self.terminate()
            elif os_type == LINUX:
                logger.logWarn(
                    "Debugger(run) is not implemented for linux platform")
            elif os_type == MAC:
                logger.logWarn(
                    "Debugger(run) is not implemented for mac platform")
            else:
                logger.logWarn(
                    "Debugger(run) is not implemented for your platform")
