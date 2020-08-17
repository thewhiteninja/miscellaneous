from pyVim import connect
from pyVmomi import vim

from VirtualMachine import *


class ExceptionInvalidCredentials(Exception):
    pass


class vSphereClient:
    def __init__(self, host="127.0.0.1", port=443, ssl=True):
        self.connected = False
        self.host = host
        self.port = port
        self.ssl = ssl
        self.instance = None

    def connect(self, username, password):
        try:
            if self.ssl:
                self.instance = connect.SmartConnect(host=self.host, user=username, pwd=password, port=self.port)
            else:
                self.instance = connect.SmartConnectNoSSL(host=self.host, user=username, pwd=password, port=self.port)
            self.connected = True
        except vim.fault.InvalidLogin:
            raise ExceptionInvalidCredentials("%s:%s" % (username, password))
        except vim.fault as message:
            raise Exception(str(message))

    def disconnect(self):
        if self.connected and self.instance is not None:
            connect.Disconnect(self.instance)
            self.connected = False

    def __del__(self):
        self.disconnect()

    def is_connected(self):
        return self.connected

    def get_vm_by_name(self, name):
        content = self.instance.RetrieveContent()
        virtual_machine = None
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        for item in container.view:
            if item.name.lower() == name.lower():
                virtual_machine = item
                break
        container.Destroy()
        if virtual_machine is not None:
            return VirtualMachine(virtual_machine, self.instance)
        return None

    def get_vm_by_uuid(self, uuid):
        content = self.instance.RetrieveContent()
        virtual_machine = content.searchIndex.FindByUuid(None, uuid, True)
        if virtual_machine is not None:
            return VirtualMachine(virtual_machine, self.instance)
        return None

    def get_vm_by_dns_name(self, name):
        content = self.instance.RetrieveContent()
        virtual_machine = content.searchIndex.FindByDnsName(None, name, True)
        if virtual_machine is not None:
            return VirtualMachine(virtual_machine, self.instance)
        return None

    def get_vm_by_ip(self, ip):
        content = self.instance.RetrieveContent()
        virtual_machine = content.searchIndex.FindByIp(None, ip, True)
        if virtual_machine is not None:
            return VirtualMachine(virtual_machine, self.instance)
        return None
