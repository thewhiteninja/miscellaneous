import urllib
import urllib2
import cookielib
import sys
import time
import platform
import getopt
import os
import re
import datetime
import sqlite3
import ConfigParser

# Megaupload.com account

mu_username = ""
mu_password = ""

# Config

(DIR, USER_AGENT, COOKIE_MU_HAPPYHOUR) = (".", "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
                                          "user=xxxxxxxxxxxxxxxxxxxxxxxxxxxx; l=fr; ver=761e40bd35a29dd83cd4ce463ab555992eae577c4d8d32420652847d38aef2a030ca78086bdf917fb63f5f6b0e5d669e7c438622039f8e4b489a272890e54c84761e40bd35a29dd83cd4ce463ab55599397f5602d02357bfea8ed3931ad2e40ef512553466b22eec94b167731800cd30; mcpop=110578-1312808550%3B108600-1312884151%3B111017-1312885353%3B109658-1312885376%3B110140-1312842192%3B58182-1312863832%3B106687-1312804846%3B")

# Global vars

mu_cookie = cookielib.MozillaCookieJar('tasks.cookies')
mu_opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
                                 urllib2.HTTPHandler(), urllib2.HTTPCookieProcessor(mu_cookie))

(LIST, FILE) = ("", "")

# Utils


def pad(s, w):
    return "0" * (len(str(w)) - s) + str(s)

##########################################################################


def downloadList(l):
    print "[+] Reading list of files",
    if not os.path.isfile(l):
        print "\t\t\t\t[ERROR]\n    Unable to read " + l
        return None
        print "\t\t\t\t[OK]"

    f = open(l, 'r')
    listOfLink = listOfLink = re.findall(
        "http://www.megaupload.com/\?d=[A-Z0-9]{8}", f.read(), re.IGNORECASE)
    f.close()

    print "    " + str(len(listOfLink)) + " file(s) found"

    downdir = os.path.normpath(DIR)
    if not os.path.isdir(downdir):
        os.makedirs(downdir)

    (count, countdl, countinv, countunav, size) = (
        len(listOfLink), 0, 0, 0, len(str(len(listOfLink))))
    for i in range(len(listOfLink)):
        if countdl > 0 and countdl % 50 == 0:
            print "    100 files have been downloaded, waiting 30 seconds ..."
            time.sleep(30)
        print "    Link " + pad(i + 1, 3) + "/" + str(count) + " : " + listOfLink[i]
        res = downloadFile(listOfLink[i], False)
        if res == 0:
            countdl += 1
        else:
            if res == 1:
                countinv += 1
                f = open(l[0:-4] + ".invalid.txt", 'a+')
            elif res == 2:
                countunav += 1
                f = open(l[0:-4] + ".unavailable.txt", 'a+')
            f.write(listOfLink[i] + '\n')
            f.close()
    print "    ----------------\n    " + pad(countdl, size) + "/" + str(count) + " files downloaded \t(" + (str(round(100.00 * countdl / count, 2)) if count > 0 and countdl > 0 else "0.00") + "%)"
    print "    " + pad(countunav, size) + "/" + str(count) + " files unavailable \t(" + (str(round(100.00 * countunav / count, 2)) if count > 0 and countunav > 0 else "0.00") + "%)"
    print "    " + pad(countinv, size) + "/" + str(count) + " files invalid \t(" + (str(round(100.00 * countinv / count, 2)) if count > 0 and countinv > 0 else "0.00") + "%)"


def reporthook(blocks_read, block_size, total_size):
    amount_read = blocks_read * block_size
    if total_size >= 0:
        print '    %d/%d' % (amount_read, total_size)


def downloadFile(link, standalone):
    if standalone:
        print "[+] Downloading " + link
    req = urllib2.Request(link)
    if len(COOKIE_MU_HAPPYHOUR) > 0:
        req.add_header('Cookie', COOKIE_MU_HAPPYHOUR)
    req.add_header('Referer', link)
    req.add_header('User-agent', USER_AGENT)
    source = mu_opener.open(req).read()
    premium = True
    start = source.find('<div class="down_ad_pad1">')
    if start == -1:
        premium = False
        start = source.find('<div class="down_butt_bg3">')
        if start == -1:
            print "    File is not available !"
            print source
            return 2

    realLink = source[source.find("http", start):source.find(
        '"', source.find("http", start))]

    if not premium:
        timetowait = source[source.find(
            "count=", start) + 6:source.find(';', source.find("count=", start))]
        print "    Waiting " + timetowait + " secs ..."
        time.sleep(int(timetowait) + 1)

    filename = realLink.split('/')[-1]
    print '    Downloading ' + filename
    try:
        urllib.urlretrieve(realLink, DIR + filename, reporthook)
        return 0
    except urllib2.URLError, e:
        print "    Error : " + e.reason
        if os.path.exists(DIR + filename):
            os.remove(DIR + filename)
        return 1


def checkHappyHour():
    h = datetime.datetime.now().hour
    m = datetime.datetime.now().minute
    if h >= 4 and h <= 14:
        if h == 4:
            return m > 30
        elif h == 14:
            return m < 45
        return True
    return False


def connectToMu():
    global COOKIE_MU_HAPPYHOUR
    print "[+] Logging in Megaupload.com",
    req = urllib2.Request("http://www.megaupload.com/?c=login", urllib.urlencode(
        {'username': mu_username, 'password': mu_password, 'login': 1, 'redir': 1}))
    req.add_header('User-agent', USER_AGENT)
    response = mu_opener.open(req)
    if response.code == 200:
        for cookie in mu_cookie:
            if cookie.name == "user":
                print "\t\t\t[SUCCESS]"
                if not checkHappyHour():
                    COOKIE_MU_HAPPYHOUR = ""
                    print "    HappyHour is currently not activated"
                return True
    print "\t\t\t[ERROR]"
    return False


def logoutToMu():
    print "[+] Logging out Megaupload.com",
    req = urllib2.Request("http://www.megaupload.com/?login=1",
                          urllib.urlencode({'logout': 1}))
    req.add_header('User-agent', USER_AGENT)
    mu_opener.open(req)
    mu_cookie.clear_session_cookies()
    print "\t\t\t[OK]"

##########################################################################


def options():
    global FILE, LIST, DIR
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:hl:f:", [
                                   "dir", "help", "list", "file"])
    except getopt.error, msg:
        print msg
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-d", "--dir"):
            DIR = a
        elif o in ("-f", "--file"):
            FILE = a
        elif o in ("-l", "--list"):
            LIST = a

    DIR = os.path.normpath(DIR)
    if not os.path.isdir(DIR):
        os.makedirs(DIR)
    DIR = DIR + os.sep


def start():
    if connectToMu():
        if len(LIST) > 0:
            downloadList(LIST)
        elif len(FILE) > 0:
            downloadFile(FILE, True)
        logoutToMu()


def usage():
    print "Usage : " + os.path.basename(sys.argv[0]) + " [Options]"
    print ""
    print "Options:"
    print "    -h|--help              : Show help"
    print "    -d|--dir  dir          : Destination folder"
    print "    -f|--file file         : Download a file"
    print "    -l|--list file         : Download a list of file"
    print ""
    print "Example : " + os.path.basename(sys.argv[0]) + " --file malist.txt"
    sys.exit(0)

if __name__ == '__main__':
    options()
    if FILE == "" and LIST == "":
        usage()
    else:
        start()
