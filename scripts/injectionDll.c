#include <common.h>
#include <injectionDll.h>
#include <windows.h>
#include <stdlib.h>
#include <string.h>

int InjectDll(long pid, char* PathDll){
    LPVOID data;
	DWORD idThread ;
	LPTHREAD_START_ROUTINE addrLoadLibrary;
    HANDLE hThread;
	long PathDllLen = strlen(PathDll) + 1;
    HANDLE hProcess = fOpenProcess(PROCESS_ALL_ACCESS , FALSE , pid);


    if(hProcess == NULL)return 3;
    data = fVirtualAllocEx( hProcess , NULL , PathDllLen , MEM_COMMIT , PAGE_EXECUTE_READWRITE);
    if(data == NULL) return 2;
    if (!fWriteProcessMemory( hProcess , data , PathDll , PathDllLen , 0)) return 0;

    addrLoadLibrary = (LPTHREAD_START_ROUTINE)fGetProcAddress(LoadLibrary("kernel32"),"LoadLibraryA");
    hThread = fCreateRemoteThread( hProcess , NULL , 0 , addrLoadLibrary , data , 0 , &idThread );
    if(hThread == NULL) return 1;
    WaitForSingleObject(hThread,INFINITE);
    fVirtualFreeEx( hProcess , data , 0 , MEM_DECOMMIT);
    CloseHandle(hProcess);
    CloseHandle(hThread);
    return 0;
}




