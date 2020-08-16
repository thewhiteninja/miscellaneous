import getopt
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from xml.dom.minidom import parseString

import dns.resolver
import dns.zone

listdnsservers = []
targetDomain = ""
targetTDL = ""
useGoogle, useBruteSub, useDNS, useRIPE = False, False, False, False
headers = { 'User-Agent': 'Mozilla 5.10' }
timeBetweenTwoGoogleRequestInSec = 2


def googleScrap(type, expr):
    subdomains = set()
    lastSize = -1
    while len(subdomains) != lastSize:
        lastSize = len(subdomains)
        neg = ''.join(['+-' + d for d in subdomains])
        try:
            request = urllib.request.Request(
                'http://google.fr/search?num=100&q=' + type + ':' + targetDomain + '.' + targetTDL + neg, None, headers)
            response = urllib.request.urlopen(request)
            for domain in expr.findall(response.read()):
                subdomains.add(domain[0])
            time.sleep(timeBetweenTwoGoogleRequestInSec)
        except KeyboardInterrupt:
            log("[!]-Interrupted by user")
            break
        except:
            break
    log("[+] Results : " + str(len(subdomains)) + " domains found")
    if "localhost" in subdomains:
        subdomains.remove("localhost")
    for subdomain in subdomains:
        print((subdomain + targetDomain + "." + targetTDL).lower())


def googleDirectWebsiteSearchWithSpecificTDLs():
    global targetTDL
    log("[+] Searching with Google with \"site:" + targetDomain + ".?\"...")
    tmptargetTDL = targetTDL
    for targetTDL in [x.lower().strip() for x in open("toplevellist.txt", "r").readlines()]:
        log("[-]    Test for : " + targetTDL)
        googleScrap("site", re.compile('(\w+\.)?(' + targetDomain + ')(\.' + targetTDL + ')+', re.IGNORECASE))
    targetTDL = tmptargetTDL


def googleDirectWebsiteSearchWithSpecificTDL():
    log("[+] Searching with Google with \"site:" + targetDomain + "." + targetTDL + "\" ...")
    googleScrap("site", re.compile('(\w+\.)?(' + targetDomain + ')(\.' + targetTDL + ')+', re.IGNORECASE))


def googleindirectwebsitesearch():
    log("\n[+] Searching with Google with \"allinurl:" + targetDomain + "." + targetTDL + "\" ...")
    googleScrap("allinurl", re.compile('(\w+\.)?(' + targetDomain + ')(\.' + targetTDL + ')+', re.IGNORECASE))


def targetDns():
    listdnsservers = dns.resolver.query(targetDomain + '.' + targetTDL, 'NS')
    log("[+] Getting DNS servers for " + targetDomain + '.' + targetTDL + " ... " + str(len(listdnsservers)) + " found")
    log("[+] Getting subdomains ...")
    for mydns in listdnsservers:
        log("[-]  using DNS server : " + str(mydns))
        myip = socket.gethostbyname(str(mydns))
        domains = set()
        try:
            z = dns.zone.from_xfr(dns.query.xfr(myip, targetDomain + '.' + targetTDL))
            for n in list(z.nodes.keys()):
                d = z[n].to_text(n)
                if d.find("IN CNAME") > 0:
                    domains.add(d.split(" ")[0] + '.' + targetDomain + '.' + targetTDL)
                    domains.add(d.split(" ")[-1])
                else:
                    for dom in re.compile('([\w-]+\.)*(' + targetDomain + ')(\.' + targetTDL + ')+',
                                          re.IGNORECASE).findall(d):
                        domains.add(dom)
        except:
            log("[x]   Zone transfert failed")
    log("[+] Results : " + str(len(domains)) + " subdomains found\n")
    if "localhost" in domains:
        domains.remove("localhost")
    for d in domains:
        print(d)


def targetDnsBF():
    print("[-]-Brute forcing...")
    for host in open("hosts.txt", "r").readlines():
        host = host.strip() + "." + targetDomain + "." + targetTDL
        try:
            answers_IPv4 = dns.resolver.query(host, 'A')
            for rdata in answers_IPv4:
                print(host, rdata.address)
        except KeyboardInterrupt:
            log("[!]-Interrupted by user")
            break
        except:
            pass


def targetRIPE():
    log("[+] Getting netblock from RIPE database ...")
    request = urllib.request.Request(
        'http://apps.db.ripe.net/whois/search?source=ripe&source=apnic&query-string=' + targetDomain +
        '&type-filter=inetnum',
        None, headers)
    netblocks = set()
    try:
        response = urllib.request.urlopen(request).read()
        dom = parseString(response)
        attributes = dom.getElementsByTagName('attribute')
        for attribute in attributes:
            if attribute.getAttribute('name') == 'inetnum':
                netblocks.add(attribute.getAttribute('value'))
    except KeyboardInterrupt:
        log("[!]-Interrupted by user")
    except:
        pass
    log("[+] Results : " + str(len(netblocks)) + " netblocks found\n")
    for block in netblocks:
        print(block)


def log(s=""):
    sys.stderr.write(s + "\n")


def run():
    log()
    log("Target : %s%s" % (targetDomain, '.' + targetTDL if targetTDL != None else ""))
    log()
    if useDNS:
        if targetTDL == None:
            log("Error : Domain name with TDL required for DNS enum")
            sys.exit(1)
        targetDns()
    if useRIPE:
        targetRIPE()
    if useBruteSub:
        if targetTDL == None:
            log("Error : Domain name with TDL required for bruteforcing subdomains")
            sys.exit(1)
        targetDnsBF()
    if useGoogle:
        if targetTDL != None:
            googleDirectWebsiteSearchWithSpecificTDL()
            googleindirectwebsitesearch()
        else:
            googleDirectWebsiteSearchWithSpecificTDLs()


def help():
    log()
    log("Usage : " + os.path.basename(sys.argv[0]) + " [options] url|domain")
    log()
    log("    Options :")
    log("        -g | --google   : use Google")
    log("        -n | --dns      : use DNS NS and AXFR")
    log("        -r | --ripe     : use RIPE Database")
    log("        -b | --dnsbrute : bruteforce subdomain")
    log("        -v | --version  : show version")
    log("        -h | --help")
    log()
    sys.exit(0)


def getDomain(url):
    if url != None:
        pat = r'((https?):\/\/)?((?P<subdomain>\w+)\.)*(?P<domain>[\w-]+)(\.(?P<tdl>\w+))?(\/.*)?'
        m = re.match(pat, url)
        if m:
            if m.group('tdl') == None:
                if m.group('subdomain') == None:
                    domain = m.group('domain')
                    tdl = None
                else:
                    domain = m.group('subdomain')
                    tdl = m.group('domain')
            else:
                domain = m.group('domain')
                tdl = m.group('tdl')
            return (domain, tdl)
        else:
            log("Error : Unable to extract a domain name from \"" + url + "\"")
            sys.exit(1)


def readOptions():
    global targetDomain, targetTDL, useGoogle, useDNS, useBruteSub, useRIPE
    options, remainder = getopt.gnu_getopt(sys.argv[1:], 'vhgnbr',
                                           ['version', 'help', 'google', 'dns', 'bfsub', 'ripe'])
    for opt, arg in options:
        if opt in ('-v', '--version', '-h', '--help'):
            help()
        elif opt in ('-g', '--google'):
            useGoogle = True
        elif opt in ('-n', '--dns'):
            useDNS = True
        elif opt in ('-b', '--bfsub'):
            useBruteSub = True
        elif opt in ('-r', '--ripe'):
            useRIPE = True
    if len(remainder) > 0:
        (targetDomain, targetTDL) = getDomain(remainder[-1])
    if not (useGoogle | useDNS | useBruteSub | useRIPE):
        if (targetDomain != "" and targetTDL != ""):
            useDNS = True
        else:
            help()


if __name__ == "__main__":
    readOptions()
    run()

