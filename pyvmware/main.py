from vSphereClient import *

vc = vSphereClient(host="10.11.1.5", ssl=False)
vc.connect(username="user", password="xxxxxxxxxxxxxxxx")
if vc.is_connected():
    vm = vc.get_vm_by_name("WIN7")
    print(vm.get_name())
    print(vm.get_uuid())
    print(vm.get_path_name())
    print(vm.get_power_state())
    print(vm.get_boot_time())
    print(vm.get_host_name())
    vm.set_creds("admin", "admin")
    vm.download_file("C:\\Users\\admin\\Desktop\\test.dat", overwrite=True)
    vc.disconnect()


