#ifndef HAVE_REMOTE
#define HAVE_REMOTE
#endif

#include <stdio.h>
#include <time.h>
#include <stdint.h>

#include "pcap.h"

#pragma comment(lib,"wpcap.lib")
#pragma comment(lib,"ws2_32.lib")

///////////////////////////////////////////////////////////////////////////////


#define ETH_FRAME_IPV4						0x0008
#define ETH_FRAME_IPV6						0xDD86

#define IP_PROTO_TCP						6
#define IP_PROTO_UD							17
	
#define SMB_COM_TRANSACTION2				0x32
#define SMB_TRANSACTION2_SESSION_SETUP		0x000e

#define NT_STATUS_NOT_IMPLEMENTED           0xc0000002


///////////////////////////////////////////////////////////////////////////////

#pragma pack(push,1)

typedef struct ip_address
{
    uint8_t byte1;
    uint8_t byte2;
    uint8_t byte3;
    uint8_t byte4;
}ip_address;

typedef struct eth_header
{
    u_int8_t		dst[6];
    u_int8_t		src[6];
    u_int16_t	type;
} eth_header;

typedef struct ipv4_header
{
    uint8_t		ver_ihl;        
    uint8_t		tos;            
    uint16_t		tlen;           
    uint16_t		identification; 
    uint16_t		flags_fo;       
    uint8_t		ttl;            
    uint8_t		proto;          
    uint16_t		crc;            
    ip_address	saddr;
    ip_address	daddr;
    uint32_t		op_pad;
} ipv4_header;

typedef struct tcp_header
{
    unsigned short src_port;    
    unsigned short dest_por;    
    unsigned long  seq_num;     
    unsigned long  ack_num;     
    unsigned short lenflags;    
    unsigned short window_size; 
    unsigned short tcp_checksum;
    unsigned short tcp_urgentptr;
} tcp_header;

typedef struct smb_header
{
    u_int32_t      netbios_session_service;
    u_int8_t       protocol[4];
    u_int8_t       command;
    u_int32_t      status;
    u_int8_t       flags;
    u_int16_t      flags2;
    u_int16_t      pid_high;
    u_int8_t       signature[8];
    u_int16_t      unused;
    u_int16_t      tid;
    u_int16_t      pid;
    u_int16_t      uid;
    u_int16_t      mid;

} smb_header;

typedef struct smb_trans2_req
{
    uint8_t       wct;
    uint16_t      total_param_count;
    uint16_t      total_data_count;
    uint16_t      max_param_count;
    uint16_t      max_data_count;
    uint8_t       max_setup_count;
    uint8_t       reserved;
    uint16_t      flags;
    uint32_t      timeout;
    uint16_t      reserve2;
    uint16_t      param_count;
    uint16_t      param_offset;
    uint16_t      data_count;
    uint16_t      data_offset;
    uint8_t       setup_count;
    uint8_t       reserved3;
    uint16_t      cmd;
    uint16_t      bct;
    uint8_t       padding[3];
    uint8_t*      payload;
} smb_trans2_req;

#pragma pack(pop)

///////////////////////////////////////////////////////////////////////////////


void print_timestamp(const struct pcap_pkthdr *header)
{
    struct tm ltime;
    time_t local_tv_sec;
    char timestr[16];

    local_tv_sec = header->ts.tv_sec;
    localtime_s(&ltime, &local_tv_sec);
    strftime(timestr, sizeof timestr, "%H:%M:%S", &ltime);

    printf("%s.%-6d ", timestr, header->ts.tv_usec);
}

void print_ip_port(ip_address addr, u_short port)
{
	char tmp[32] = {0};
    sprintf_s(tmp, 32, "%d.%d.%d.%d:%-5d", addr.byte1, addr.byte2, addr.byte3, addr.byte4, port);
    printf("%21s", tmp);
}

void packet_handler(u_char *param, const struct pcap_pkthdr *header, const u_char *pkt_data)
{
    (void*)param;

    eth_header *eth = (eth_header *)(pkt_data);

    if (eth->type == ETH_FRAME_IPV4)
    {
        ipv4_header *ih = (ipv4_header*)(pkt_data + sizeof(eth_header));
        u_int ip_len = (ih->ver_ihl & 0xf) * 4;

        if (ih->proto == IP_PROTO_TCP)
        {
            tcp_header *tcp = (tcp_header*)(pkt_data + sizeof(eth_header) + ip_len);
            u_int32_t tcp_len = ((tcp->lenflags & 0x00f0) >> 4) * 4;

            u_short sport = ntohs(tcp->src_port);
            u_short dport = ntohs(tcp->dest_por);

            uint32_t payload_len = ntohs(ih->tlen) - ip_len - tcp_len;

			// SMB Request
            if (dport == 445 && payload_len > 0)
            {
                smb_header* smb_h = (smb_header*)(pkt_data + sizeof(eth_header) + ip_len + tcp_len);
                
                if (smb_h->command == SMB_COM_TRANSACTION2 && !(smb_h->flags & 0x80))
                {
                    smb_trans2_req* t2req = (smb_trans2_req*)(pkt_data + sizeof(eth_header) + ip_len + tcp_len + sizeof(smb_header));

                    if (t2req->cmd == SMB_TRANSACTION2_SESSION_SETUP)
                    {

                        print_timestamp(header);
                        print_ip_port(ih->saddr, sport); printf(" -> "); print_ip_port(ih->daddr, dport);
                        printf(" - DoublePulsar Backdoor Test\n");

                    }
                }                
            }
            
			// SMB Response
			if (sport == 445 && payload_len > 0)
            {
                smb_header* smb_h = (smb_header*)(pkt_data + sizeof(eth_header) + ip_len + tcp_len);

                if (smb_h->command == SMB_COM_TRANSACTION2 && (smb_h->flags & 0x80))
                {
                    if (smb_h->status == NT_STATUS_NOT_IMPLEMENTED)
                    {
                        if (smb_h->mid == 0x51)
                        {
                            print_timestamp(header);
                            print_ip_port(ih->saddr, sport);  printf(" -> "); print_ip_port(ih->daddr, dport);
                            printf(" - DoublePulsar Backdoor Response (INFECTED)\n");
                        }
                    }                    
                }
            }
        }
    }
}


///////////////////////////////////////////////////////////////////////////////


void list_interfaces()
{
    int i = 0;
    pcap_if_t *alldevs;
    char errbuf[PCAP_ERRBUF_SIZE];

    printf("[+] Interface list\n");

    if (pcap_findalldevs_ex(PCAP_SRC_IF_STRING, NULL, &alldevs, errbuf) == -1)
    {
        fprintf(stderr, "[!] Error in pcap_findalldevs: %s\n", errbuf);
        exit(1);
    }

    for (pcap_if_t *d = alldevs; d; d = d->next)
    {
        printf("    %d - %s", ++i, d->name);
        if (d->description)
            printf(" (%s)\n", d->description);
        else
            printf(" (No description available)\n");
    }

    if (i == 0)
    {
        printf("[+] No interfaces found !.\n");
    }

    pcap_freealldevs(alldevs);
}


pcap_t* capture_from_interface(uint32_t interface_id)
{
    pcap_t* handle = NULL;
    pcap_if_t *alldevs;
    char errbuf[PCAP_ERRBUF_SIZE];

    if (pcap_findalldevs_ex(PCAP_SRC_IF_STRING, NULL, &alldevs, errbuf) == -1)
    {
        fprintf(stderr, "[!] Error in pcap_findalldevs: %s\n", errbuf);
        exit(1);
    }

    uint32_t max_devid = 0;
    pcap_if_t *d = alldevs;
    while (d->next) { max_devid++; d = d->next; }

    if (interface_id < 1 || interface_id > max_devid)
    {
        printf("[!] Interface number out of range.\n");
        pcap_freealldevs(alldevs);
        return NULL;
    }

    for (d = alldevs; max_devid > 0; max_devid--);

    if ((handle = pcap_open(d->name, 65536, PCAP_OPENFLAG_PROMISCUOUS, 1000, NULL, errbuf)) == NULL)
    {
        fprintf(stderr, "[!] Unable to open the adapter. %s is not supported by WinPcap\n", d->name);
        pcap_freealldevs(alldevs);
        return NULL;
    }

    printf("[+] Listening on %s...\n", d->description);
    pcap_freealldevs(alldevs);

    return handle;
}

pcap_t* capture_from_pcap_file(char* path)
{
    pcap_t *fp = NULL;
    char errbuf[PCAP_ERRBUF_SIZE] = { 0 };
    char source[PCAP_BUF_SIZE] = { 0 };

    if (pcap_createsrcstr(source, PCAP_SRC_FILE, NULL, NULL, path, errbuf) != 0)
    {
        fprintf(stderr, "[!] Error creating a source string from given filepath.\n");
        return NULL;
    }

    if ((fp = pcap_open(source, 65536, PCAP_OPENFLAG_PROMISCUOUS, 1000, NULL, errbuf)) == NULL)
    {
        fprintf(stderr, "[!] Error opening %s.\n", source);
        return NULL;
    }

    return fp;
}




///////////////////////////////////////////////////////////////////////////////

void usage(char** argv)
{
    printf("DoublePulsar Detector\n\n");
    printf("Usage: %s options\n\n", argv[0]);
    printf("    Options:\n");
    printf("    --help/-h              : Show this message\n");
    printf("    --list                 : List all interfaces\n");
    printf("    --live [interface_num] : Capture packets from an interface\n");
    printf("    --file [filename]      : Capture packets from a file\n\n");

    exit(2);
}


int main(int argc, char ** argv)
{
    pcap_t* handle = NULL;

    if (argc < 2) usage(argv);

    if (!strcmp(argv[1], "--list"))
    {
        list_interfaces();
    }
    else if (!strcmp(argv[1], "--help") || !strcmp(argv[1], "-h"))
    {
        usage(argv);
    }
    else if (!strcmp(argv[1], "--file"))
    {
        if (2 < argc)
        {
            handle = capture_from_pcap_file(argv[2]);
        }
        else
        {
            usage(argv);
        }
    }
    else if (!strcmp(argv[1], "--live"))
    {
        if (2 < argc)
        {
            uint32_t id = atoi(argv[2]);
            handle = capture_from_interface(id);
        }
        else
        {
            usage(argv);
        }
    }
    else usage(argv);

    if (handle) 	pcap_loop(handle, 0, packet_handler, NULL);

    return 0;
}
