class DebuggerProcess:
    def __init__(self):
        self.pid = -1
        self.process_handle = -1
        self.dirty_memory = False