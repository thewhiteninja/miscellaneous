from modules.windows.defines import ProcessInfo


class DebuggerProcess:

    def __init__(self):
        self.info = ProcessInfo()
        self.info.hProcess = -1
        self.info.hThread = -1
        self.info.dwProcessId = -1
        self.info.dwThreadId = -1
        self.dirty_memory = False
