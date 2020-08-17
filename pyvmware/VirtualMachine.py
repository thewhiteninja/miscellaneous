import os

import requests
from pyVmomi import vim
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from GuestMachine import *
from utils import wait_for_tasks


class VM_PowerState(Enum):
    OFF = 0
    ON = 1,
    SUSPENDED = 2


class VirtualMachine:

    def __init__(self, vm, si):
        assert vm is not None
        assert si is not None
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.vm = vm
        self.si = si
        self.creds = None

    def set_creds(self, username, password):
        self.creds = (username, password)

    def get_name(self):
        return self.vm.summary.config.name

    def get_uuid(self):
        return self.vm.summary.config.instanceUuid

    def get_path_name(self):
        return self.vm.summary.config.vmPathName

    def get_power_state(self):
        if self.vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
            return VM_PowerState.OFF
        elif self.vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
            return VM_PowerState.ON
        elif self.vm.runtime.powerState == vim.VirtualMachinePowerState.suspended:
            return VM_PowerState.SUSPENDED

    def get_boot_time(self):
        return self.vm.runtime.bootTime

    def get_host_name(self):
        return self.vm.runtime.host.name

    def reboot_hard(self):
        wait_for_tasks(self.si, [self.vm.ResetVM_Task()])

    def reboot_soft(self):
        self.vm.soft_reboot()

    def power_on(self):
        wait_for_tasks(self.si, [self.vm.PowerOn_Task()])

    def power_off(self):
        wait_for_tasks(self.si, [self.vm.PowerOff_Task()])

    @property
    def guest(self):
        return GuestMachine(self.vm.guest)

    @guest.setter
    def guest(self, value):
        raise Exception("Invalid action")

    def download_file(self, guest_path, output_dir=".", overwrite=False):
        if self.guest.get_tools_status() != VM_ToolsStatus.OK:
            raise Exception("VMwareTools is either not running or not installed. "
                            "Rerun the script after verifying that VMWareTools "
                            "is running")

        if self.creds is None:
            raise Exception("Credentials must be set before calling this function.")

        creds = vim.vm.guest.NamePasswordAuthentication(username=self.creds[0], password=self.creds[1])
        content = self.si.RetrieveContent()
        transfert = content.guestOperationsManager.fileManager.InitiateFileTransferFromGuest(self.vm, creds, guest_path)

        resp = requests.get(transfert.url, verify=False)
        if not resp.status_code == 200:
            raise Exception("Error while downloading file (code:%d)" % resp.status_code)
        else:
            output_path = os.path.join(output_dir, os.path.basename(guest_path))
            if overwrite or not os.path.exists(output_path):
                f = open(output_path, "wb")
                f.write(resp.content)
                f.close()
