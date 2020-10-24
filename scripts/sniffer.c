#include <winsock2.h>
#include <windows.h>
#include <stdio.h>

#define SIO_RCVALL _WSAIOW(IOC_VENDOR,1)
#define RCVALL_ON 1
#define RCVALL_OFF 0

typedef struct iphdr{
  unsigned char  IHL:4;  			// 4-bit header length (in 32-bit words)
									// normally=5 (Means 20 Bytes may be 24 also)
  unsigned char  Version   :4;  	// 4-bit IPv4 version
  unsigned char  TypeOfService;		// IP type of service
  unsigned short TotalLength;		// Total length
  unsigned short ID;            	// Unique identifier
  unsigned char  FlagOffset   :5;	// Fragment offset field
  unsigned char  MoreFragment :1;
  unsigned char  DontFragment :1;
  unsigned char  ReservedZero :1;
  unsigned char  FragOffset;   		//fragment offset
  unsigned char  Ttl;           	// Time to live
  unsigned char  Protocol;      	// Protocol(TCP,UDP etc)
  unsigned short Checksum;      	// IP checksum
  unsigned int   Source;       		// Source address
  unsigned int   Destination;       // Destination address
}IP_HDR;

typedef struct tcphdr{
    unsigned short PortSource;
    unsigned short PortDest;
    unsigned int seqnum;
    unsigned int acknum;
    unsigned char unused:4, tcp_hl:4;
    unsigned char flags;
    unsigned short window;
    unsigned short checksum;
    unsigned short urgPointer;
} TCP_HDR;

static WSADATA wsa;
static SOCKET sock;
static SOCKADDR_IN sin;
static HANDLE hThread;

static DWORD WINAPI SnifferProc(LPVOID lpParam) {
	char ip[100];
	unsigned short portS, portD;
	char trame[4096];
	DATA_BLOB data;
	int size;

    IP_HDR* HeaderIP=(IP_HDR*)trame;
    TCP_HDR *HeaderTCP=(TCP_HDR*)(trame+sizeof(IP_HDR));
    data.pbData = (byte*)(trame+sizeof(TCP_HDR)+sizeof(IP_HDR));
    while (1){
        if ((size = recv((SOCKET)lpParam, trame, sizeof(trame), 0)) != -1){
        data.cbData = size - sizeof(TCP_HDR) - sizeof(IP_HDR);

        INFO("Nouveau Packet %ld", data.cbData);
        portS = ntohs(HeaderTCP->PortSource);
        portD = ntohs(HeaderTCP->PortDest);
        sprintf(ip,"%s", inet_ntoa(*(struct in_addr *)&HeaderIP->Source));
        INFO("Source : %s",ip);
        sprintf(ip,"%s", inet_ntoa(*(struct in_addr *)&HeaderIP->Destination));
        INFO("Destination : %s",ip);
        INFO("Protocol : %d", HeaderIP->Protocol);
        }
    }
    return 0;
}

int sniffer_network_init(){
    if(WSAStartup(MAKEWORD(2,2), &wsa) == 0)    {
        if((sock = socket(AF_INET, SOCK_RAW, IPPROTO_IP)) != INVALID_SOCKET)
        {
            sin.sin_family = AF_INET;
            sin.sin_addr.s_addr = INADDR_ANY;
            if(bind(sock, (SOCKADDR*)&sin, sizeof(sin)) != SOCKET_ERROR)
            {
            	DWORD dwBytesRet;
            	unsigned int option;
            	WSAIoctl(sock,SIO_RCVALL,&option,sizeof(option),NULL,0,&dwBytesRet,NULL,NULL);
                return 0;
            }
            return 3;
        }
        return 2;
    }
    closesocket(sock);
    return 1;
}

int sniffer_network_start(){
	hThread = CreateThread(NULL, 0, SnifferProc, (LPVOID) sock, 0, NULL);
	return (int)hThread;
}

void sniffer_network_free(){
	TerminateThread(hThread, 0);
	closesocket(sock);
}