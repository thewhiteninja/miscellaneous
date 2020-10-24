import os
import re
from _winreg import *

WINDOWS_SDK_KEY_PATH_64 = "SOFTWARE\\WOW6432Node\\Microsoft\\Microsoft SDKs\\Windows"
WINDOWS_SDK_KEY_PATH_32 = "SOFTWARE\\Microsoft\\Microsoft SDKs\\Windows"

WINERROR_PATH = "Include\\%s\\shared\\winerror.h"

RE_D = re.compile('\d')

def compareVersions(a, b):
    if (a[0] == "v" or b[0] == "v"):
        a = a[1:]
        b = b[1:]
    aMajor, aMinor = a.split(".")
    bMajor, bMinor = b.split(".")
    if int(aMajor) != int(bMajor):
        return aMajor < bMajor
    else:
        return aMinor < bMinor

def findLastSDKVersion():
    print "[+] Finding SDK installed folder"
    try:
        key = OpenKey(HKEY_LOCAL_MACHINE, WINDOWS_SDK_KEY_PATH_32, 0, KEY_READ)
    except:
        key = OpenKey(HKEY_LOCAL_MACHINE, WINDOWS_SDK_KEY_PATH_64, 0, KEY_READ)

    i = 0
    versions = []
    while True:
        try:
            ver = EnumKey(key, i)
            versions.append(ver)
            i += 1
        except OSError as e:
            break       
        
    CloseKey(key)
    
    print "[+] %d version(s) found" % len(versions)
    
    if len(versions) > 0:
        sorted(versions, cmp=compareVersions)    
        print "[+] Last version: %s" % versions[0]   
        return versions[0]
    else:
        return None
        
def getSDKVersionInfo(version):
    print "[+] Getting SDK version info"
    try:
        key = OpenKey(HKEY_LOCAL_MACHINE, WINDOWS_SDK_KEY_PATH_32 + "\\" + version, 0, KEY_READ)
    except:
        key = OpenKey(HKEY_LOCAL_MACHINE, WINDOWS_SDK_KEY_PATH_64 + "\\" + version, 0, KEY_READ)    
        
    i = 0
    while True:
        try:
            k, v, f = EnumValue(key, i)
            i += 1
            if k == "ProductVersion":
                DetailedVersion = v + ".0"*(4 - len(v.split(".")))
            elif k == "InstallationFolder":
                InstalledFolder = v
        except:
            break
            
    print "[+] Version : %s" % DetailedVersion
    print "[+] Install Path : %s" % InstalledFolder    
        
    CloseKey(key)    
    
    return DetailedVersion, InstalledFolder
    
def hasNumbers(inputString):
    return RE_D.search(inputString)  
    
def genHeader(path):
    print "[+] Reading", path
    f = open(path, "rb")
    header = f.readlines()
    f.close()
    
    print "======================================================"
    print 
    print "ERROR_CODES = {"
    for line in header:
        if line.startswith("#define"):
            items = line.split()
            if len(items)>2:
                name = items[1]
                value = items[2]
                if value.startswith("_HRESULT_TYPEDEF_("):
                    value = value[len("_HRESULT_TYPEDEF_("):-1]
                if value.startswith("((HRESULT)"):
                    value = value[len("((HRESULT)"):-1]
                if value.startswith("_NDIS_ERROR_TYPEDEF_("):
                    value = value[len("_NDIS_ERROR_TYPEDEF_("):-1]
                if not hasNumbers(value):
                    continue
                if value.startswith("_"):
                    continue
                print "%s : \"%s\"," % (value, name)
    print "}"
    print 
    print "def get_error_cst(e):"
    print "  if e in ERROR_CODES:"
    print "    return ERROR_CODES[e]"
    print "  else:"
    print "    return \"\""
    print 
    

def main():
    v = findLastSDKVersion()
    sdk_version, sdk_path = getSDKVersionInfo(v)
    
    winerror_path = WINERROR_PATH % sdk_version
    
    genHeader(os.path.join(sdk_path, winerror_path))

if __name__ == '__main__':
    main()