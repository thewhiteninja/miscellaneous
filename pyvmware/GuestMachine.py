from enum import Enum


class VM_ToolsStatus(Enum):
    NOT_INSTALLED = 0
    NOT_RUNNING = 1
    OK = 2
    OLD = 3


class GuestMachine:
    def __init__(self, guest):
        self.guest = guest

    def get_tools_status(self):
        st = self.guest.toolsStatus
        if st == "toolsNotInstalled":
            return VM_ToolsStatus.NOT_INSTALLED
        elif st == "toolsNotRunning":
            return VM_ToolsStatus.NOT_RUNNING
        elif st == "toolsOk":
            return VM_ToolsStatus.OK
        elif st == "toolsOld":
            return VM_ToolsStatus.OLD
