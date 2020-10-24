
#include <sendpost.h>
#include <Wininet.h>

void send_post(char* server, char* page, DATA_BLOB* data){
	char* headers = "Content-Type: application/x-www-form-urlencoded";
	const char* accept = "*/*";
	HINTERNET hSession;
	HINTERNET hConnect;
	HINTERNET hRequest;
	hSession = fInternetOpen("IE8", INTERNET_OPEN_TYPE_PRECONFIG, NULL, NULL, 0);
	if (!hSession) ERR("InternetOpen (%ld)", GetLastError());
	hConnect = fInternetConnect(hSession, server, INTERNET_DEFAULT_HTTP_PORT, NULL, NULL, INTERNET_SERVICE_HTTP, 0, 1);
	if (!hConnect) ERR("InternetConnect (%ld)", GetLastError());
	hRequest = fHttpOpenRequest(hConnect, "POST", page, NULL, NULL, (LPCSTR*)accept, 0, 1);
	if (!hRequest) ERR("HttpOpenRequest (%ld)", GetLastError());
	if (!fHttpSendRequest(hRequest, headers, strlen(headers), data->pbData, data->cbData))
		ERR("%ld", GetLastError());
	fInternetCloseHandle(hRequest);
	fInternetCloseHandle(hConnect);
	fInternetCloseHandle(hSession);
}
