import urllib
import mimetools
import urllib2
import cookielib
import sys
import time
import platform
import getopt
import os
import re
import random
import datetime
import sqlite3
import ConfigParser
import math

# Megaupload.com account

mu_username = ""
mu_password = ""

# EasyRewards.fr account

er_username = ""
er_password = ""

# Config

(DIR, USER_AGENT, COOKIE_MU_HAPPYHOUR) = (".", "", "")

# Global vars

mu_cookie = cookielib.MozillaCookieJar('tasks.cookies')
er_cookie = cookielib.MozillaCookieJar('tasks.cookies')
mu_opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
                                 urllib2.HTTPHandler(), urllib2.HTTPCookieProcessor(mu_cookie))
er_opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
                                 urllib2.HTTPHandler(), urllib2.HTTPCookieProcessor(er_cookie))

(TEST, AUTO, VALIDKEY, CHOOSEFILE, DOWNLOADLIST, DOWNLOADUNAV, OFF) = (
    False, True, False, False, False, False, False)

# Utils


def pad(s, w):
    s = math.trunc(s)
    return "0" * (w - len(str(s))) + str(s)


def toFile(data, name):
    f = open(name, 'w')
    f.write(data)
    f.close()

##########################################################################


def importCookieHH():
    global COOKIE_MU_HAPPYHOUR
    cookieHH = ""
    firefoxDir = os.path.normpath(os.environ[
                                  'APPDATA']) + os.sep + "Mozilla" + os.sep + "Firefox" + os.sep + "Profiles" + os.sep
    if os.path.isdir(firefoxDir):
        if len(os.listdir(firefoxDir)) > 0:
            profile = os.listdir(firefoxDir)[0]
            cookiesPath = firefoxDir + profile + os.sep + "cookies.sqlite"
            if os.path.isfile(cookiesPath):
                con = sqlite3.connect(cookiesPath)
                cursor = con.cursor()
                cursor.execute(
                    "SELECT name, value FROM moz_cookies WHERE host='.megaupload.com'")
                info = 0
                for cook in cursor.fetchall():
                    if cook[0] in ('l', 'user', 'ver', 'mcpop'):
                        cookieHH += cook[0] + '=' + cook[1] + '; '
                        info += 1
                if len(cookieHH) > 0:
                    cookieHH = cookieHH[0:-2]
                con.close()
                if info == 4:
                    print "    HappyHour cookie has been successfully imported !"
                    COOKIE_MU_HAPPYHOUR = cookieHH
                    config = ConfigParser.RawConfigParser()
                    config.read('EasyPoints.cfg')
                    config.set('Megaupload', 'cookieHappyHour', cookieHH)
                    f = open('EasyPoints.cfg', 'w')
                    config.write(f)
                    f.close()
                    return True
                else:
                    print "    Cookie has been found but it isn't an \"HappyHour\" cookie"
            else:
                print "    Cookie file has not been found"
    else:
        print "    Firefox directory has not been found"
    return False


def downloadList(l):
    print "[+] Reading list of files",
    day = datetime.date.today().strftime("%y%m%d")
    if l == None:
        l = day + ".txt"
    if not os.path.isfile(DIR + l):
        print "\t\t\t[ERROR]"
        return None
    print "\t\t\t[OK]"
    f = open(DIR + l, 'r+')
    listOfLink = re.findall(
        "http://www.megaupload.com/\?d=[A-Z0-9]{8}", f.read(), re.IGNORECASE)
    if l.endswith('.unavailable.txt'):
        f.seek(0, 0)
        f.truncate()
    f.close()
    print "    " + str(len(listOfLink)) + " file(s) found"
    downdir = os.path.normpath(DIR + day)
    if not os.path.isdir(downdir):
        os.makedirs(downdir)

    (count, countdl, countinv, countunav, countnokey, size, t) = (
        len(listOfLink), 0, 0, 0, 0, len(str(len(listOfLink))), time.time())
    for i in range(len(listOfLink)):
        print "    Link " + pad(i + 1, size) + "/" + str(count) + " : " + listOfLink[i]
        time.sleep(1)
        res = downloadFile(listOfLink[i])
        if res == 0:
            countdl += 1
        elif res == 3:
            countdl += 1
            countnokey += 1
        else:
            if res == 1:
                countinv += 1
                f = open(DIR + day + ".invalid.txt", 'a+')
            elif res == 2:
                countunav += 1
                f = open(DIR + day + ".unavailable.txt", 'a+')
            f.write(listOfLink[i] + '\n')
            f.close()
    print "    ----------------\n    " + pad(countdl, size) + "/" + str(count) + " file(s) downloaded  (" + (str(round(100.00 * countdl / count, 2)) if count > 0 and countdl > 0 else "0.00") + "%)"
    print "    " + pad(countnokey, size) + "/" + str(countdl) + " file(s) without key (" + (str(round(100.00 * countnokey / countdl, 2)) if countdl > 0 and countnokey > 0 else "0.00") + "%)"
    print "    " + pad(countunav, size) + "/" + str(count) + " file(s) unavailable (" + (str(round(100.00 * countunav / count, 2)) if count > 0 and countunav > 0 else "0.00") + "%)"
    print "    " + pad(countinv, size) + "/" + str(count) + " file(s) invalid     (" + (str(round(100.00 * countinv / count, 2)) if count > 0 and countinv > 0 else "0.00") + "%)"
    t = time.time() - t
    print "    ----------------\n    Time elapsed : " + pad(t / 3600, 2) + ':' + pad((t % 3600) / 60, 2) + ':' + pad(t % 60, 2)

    if countdl == count:
        if os.path.isfile(DIR + day + ".txt"):
            os.remove(DIR + day + ".txt")
        if os.path.isfile(DIR + day + ".unavailable.txt"):
            os.remove(DIR + day + ".unavailable.txt")
        if os.path.isfile(DIR + day + ".invalid.txt"):
            os.remove(DIR + day + ".invalid.txt")


def downloadFile(link):
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
            return 2

    realLink = source[source.find("http", start):source.find(
        '"', source.find("http", start))]

    if not premium:
        timetowait = source[source.find(
            "count=", start) + 6:source.find(';', source.find("count=", start))]
        print "    Waiting " + timetowait + " secs ..."
        time.sleep(int(timetowait) + 1)

    filename = realLink.split('/')[-1]
    print '    Downloading "' + filename + '"'
    try:
        key = mu_opener.open(realLink).read()
        haveKey = key.find('activation est "')
        localFile = open(
            DIR + datetime.date.today().strftime("%y%m%d") + os.sep + filename, 'w')
        if haveKey != -1:
            key = key[key.find('"', haveKey) + 2:key.find('".', haveKey) - 1]
        localFile.write(key)
        localFile.close()
        if haveKey != -1:
            return 0
        return 3
    except urllib2.URLError, e:
        print "    Error(" + str(e.code) + ") : " + e.read()
        if localFile:
            localFile.close()
        if os.path.exists(DIR + datetime.date.today().strftime("%y%m%d") + os.sep + filename):
            os.remove(
                DIR + datetime.date.today().strftime("%y%m%d") + os.sep + filename)
        return 1


def encode_multipart_formdata_for_file(filename):
    BOUNDARY = mimetools.choose_boundary()
    CRLF = '\r\n'
    CHARSET = [chr(i)
               for i in ([32] * 10 + range(65, 91) + range(97, 123) * 5)]
    L = []

    L.append('--' + BOUNDARY)
    L.append('Content-Disposition: form-data; name="multimessage_0"')
    L.append('')
    L.append(''.join([random.choice(CHARSET)
                      for i in range(random.randint(10, 30))]))

    L.append('--' + BOUNDARY)
    L.append('Content-Disposition: form-data; name="multifile_0"; filename="%s"' %
             os.path.basename(filename))
    L.append('Content-Type: application/octet-stream')

    L.append('')
    tmp = open(DIR + filename, 'r')
    L.append(tmp.read())
    tmp.close()

    L.append('--' + BOUNDARY)
    L.append('Content-Disposition: form-data; name="accept"')
    L.append('')
    L.append('on')

    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

    return content_type, body


def uploadFile(filename):
    print "    Uploading \"" + filename + "\" to MU"
    response = mu_opener.open("http://www.megaupload.com/multiupload/").read()
    uploadlink = re.compile(
        "(http://www\d+.megaupload\.com/upload_done\.php\?UPLOAD_IDENTIFIER=\d+)").search(response)
    if uploadlink:
        uploadlink = uploadlink.group(0)
        content_type, body = encode_multipart_formdata_for_file(filename)
        req = urllib2.Request(uploadlink, body)
        req.add_header('Content-Type', content_type)
        req.add_header('Content-Length', str(len(body)))
        req.add_header('User-agent', USER_AGENT)
        response = mu_opener.open(req)
        if response.code == 200:
            link = re.compile(
                "(http://www\.megaupload\.com/\?d=[0-9A-Z]+)").search(response.read())
            if link:
                print "    => " + link.group(0)
                return link.group(0)
    print "    Err : Unable to upload the file"
    return None


def checkHappyHour():
    h = datetime.datetime.now().hour
    m = datetime.datetime.now().minute
    if h >= 4 and h <= 14:
        if h == 4:
            return m > 30
        elif h == 14:
            return m < 30
        return True
    return False


def getPoints(c):
    req = urllib2.Request("http://tagup.megaupload.com/?c=rewards")
    req.add_header('Cookie', 'l=fr; user=' + c)
    req.add_header('User-agent', USER_AGENT)
    response = mu_opener.open(req).read()
    points = re.search("Vous avez (\d+) points", response)
    if points != None:
        return points.group(1)
    return None


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
                print "\t\t\t[OK]"
                points = getPoints(cookie.value)
                if points:
                    print "    You have " + points + " MU points"
                else:
                    print "    Unable to get your MU points"
                if not checkHappyHour():
                    COOKIE_MU_HAPPYHOUR = ""
                    print "    HappyHour is currently not activated"
                else:
                    print "    HappyHour is currently activated"
                return True
    print "\t\t\t[ERROR]\n    Please check your credentials for Megaupload.com"
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


def connectToEr():
    print "[+] Logging in EasyRewards.fr",
    data = urllib.urlencode(
        {'nom': er_username, 'pass': er_password, 'seconnecter': 'Se connecter'})
    req = urllib2.Request("http://www.easyrewards.fr/connexion.php", data)
    req.add_header('User-agent', USER_AGENT)
    response = er_opener.open(req)
    if response.code == 200:
        if response.read().find('URL=suivi.php') != -1:
            print "\t\t\t[OK]"
            return True
    print "\t\t\t[ERROR]"
    return False


def keyIsAvailable():
    print "[+] Checking if key is needed",
    req = urllib2.Request("http://www.easyrewards.fr/suivi.php")
    req.add_header('User-agent', USER_AGENT)
    response = er_opener.open(req).read()
    keyword = response.find('Vous trouverez la')
    if keyword != -1:
        keyword = response[response.find(
            '"', keyword) + 1:response.find('".', keyword)]
        print "\t\t\t[YES]\n    Key is in \"" + keyword + "\""
        return keyword
    else:
        print "\t\t\t[NO]"
        return None


def getKey(f):
    key = None
    try:
        localFile = open(DIR + (datetime.date.today() -
                                datetime.timedelta(days=2)).strftime("%y%m%d") + os.sep + f, 'r')
        key = localFile.read()
        localFile.close()
        print '    Key is "' + key + '"'
    except IOError:
        print '    Unable to find/read "' + f + '"'
    return key


def addFileToManager(link, name):
    print "    Adding link to the link manager"
    data = urllib.urlencode({'url': link, 'btajoutfichier': 'Valider'})
    req = urllib2.Request(
        "http://www.easyrewards.fr/gestion.php?gestionnaire", data)
    req.add_header('User-agent', USER_AGENT)
    response = er_opener.open(req).read()
    if response.find('est plus disponible') != -1:
        print "    Warn : The file seems to be unavailable :("
        print "    Waiting 30 secs ..."
        time.sleep(30)
        return addFileToManager(link, name)
    elif response.find(link) != -1:
        return True
    else:
        print "    Err : Unable to add the file to the manager"
        return False


def cleanFiles():
    print "    Removing old files"
    day = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%y%m%d")
    for afile in os.listdir(DIR + day):
        os.remove(DIR + day + os.sep + afile)
    os.rmdir(DIR + day)
    for afile in os.listdir(DIR):
        if afile.startswith(day):
            os.remove(DIR + afile)


def validKey(k):
    if k != None:
        data = urllib.urlencode(
            {'cleactivation': k, 'btvalidationcleactivation': 'Valider la clé d\'activation'})
        req = urllib2.Request("http://www.easyrewards.fr/suivi.php", data)
        req.add_header('User-agent', USER_AGENT)
        response = er_opener.open(req).read()
        if response.find('licitation'):
            print "    Key has been validated"
            # cleanFiles()
            return True
    print "    Key has not been validated"
    return False


def listIsAvailable():
    print "[+] Checking if a new filelist is available",
    req = urllib2.Request("http://www.easyrewards.fr/suivi.php")
    req.add_header('User-agent', USER_AGENT)
    response = er_opener.open(req).read()
    if response.find('Merci, vous aurez donc') == -1:
        if response.find('chargez la liste des fichiers du jour') != -1:
            print "\t[YES]"
            return True
    print "\t[NO]"
    return False


def downloadFilelist():
    print "    Downloading new filelist",
    req = urllib2.Request("http://www.easyrewards.fr/dl.php")
    req.add_header('User-agent', USER_AGENT)
    response = er_opener.open(req)
    if response.code == 200:
        localFile = open(
            DIR + datetime.date.today().strftime("%y%m%d") + ".txt", 'w')
        localFile.write(response.read())
        localFile.close()
        print "\t\t\t[OK]"
        return datetime.date.today().strftime("%y%m%d") + ".txt"
    print "\t\t\t[ERROR]"
    return None


def needToChooseFile():
    print "[+] Checking if a new file is needed",
    req = urllib2.Request("http://www.easyrewards.fr/suivi.php")
    req.add_header('User-agent', USER_AGENT)
    response = er_opener.open(req).read()
    if response.find('Merci de selectionner le fichier que vous souhaitez poster') != -1:
        print "\t\t[YES]"
        return True
    print "\t\t[NO]"
    return False


def getGeneratedFile():
    print "    Downloading new generated file"
    req = urllib2.Request("http://www.easyrewards.fr/generateur.php")
    req.add_header('User-agent', USER_AGENT)
    response = er_opener.open(req)
    localName = response.info()['Content-Disposition'].split('filename=')[1]
    if localName[0] == '"' or localName[0] == "'":
        localName = localName[1:-1]
    localFile = open(DIR + localName, 'w')
    localFile.write(response.read())
    localFile.close()
    if len(localName) > 0:
        print "    Name is \"" + localName + "\""
        return localName
    print "    Err : Unable to download the file"
    return None


def chooseFile(link):
    print "    Choosing the new file as the next file"
    data = urllib.urlencode({'url': link, 'btfchiermu': ' Valider '})
    req = urllib2.Request("http://www.easyrewards.fr/suivi.php", data)
    req.add_header('User-agent', USER_AGENT)
    response = er_opener.open(req).read()
    if response.find('Merci de selectionner le fichier que vous souhaitez poster') == -1:
        return True
    else:
        print "    Err : Unable to choose the file as the next file"
        return False


def logoutToEr():
    print "[+] Logging out EasyRewards.fr",
    req = urllib2.Request("http://www.easyrewards.fr/deconnexion.php")
    req.add_header('User-agent', USER_AGENT)
    er_opener.open(req)
    er_cookie.clear_session_cookies()
    print "\t\t\t[OK]"

##########################################################################


def shutdown():
    if platform.system() == "Windows":
        os.system('shutdown -s -t 5')
    else:
        os.system('shutdown -h now')


def loadConfig():
    global mu_username, mu_password, er_username, er_password, COOKIE_MU_HAPPYHOUR, USER_AGENT
    print "[+] Reading configuration file",
    config = ConfigParser.RawConfigParser()
    config.read('EasyPoints.cfg')
    try:
        mu_username = config.get('Megaupload', 'username')
        mu_password = config.get('Megaupload', 'password')
        er_username = config.get('EasyRewards', 'username')
        er_password = config.get('EasyRewards', 'password')
        COOKIE_MU_HAPPYHOUR = config.get('Megaupload', 'cookieHappyHour')
        USER_AGENT = config.get('EasyPoints', 'useragent')
        print "\t\t\t[OK]"
        return True
    except:
        print "\t\t\t[ERROR]\n    Unable to read EasyPoints.cfg"
        return False


def options():
    global DIR, TEST, AUTO, VALIDKEY, CHOOSEFILE, DOWNLOADLIST, DOWNLOADUNAV, OFF
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:hts", [
                                   "dir", "help", "test", "shutdown", "validkey", "choosefile", "downloadlist", "downloadunav"])
    except getopt.error, msg:
        print msg
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-d", "--dir"):
            DIR = a
        elif o in ("-t", "--test"):
            TEST = True
        elif o in ("-s", "--shutdown"):
            OFF = True
        elif o in ('--validkey'):
            AUTO = False
            VALIDKEY = True
        elif o in ('--choosefile'):
            AUTO = False
            CHOOSEFILE = True
        elif o in ('--downloadlist'):
            AUTO = False
            DOWNLOADLIST = True
        elif o in ('--downloadunav'):
            AUTO = False
            DOWNLOADUNAV = True

    DIR = os.path.normpath(DIR)
    if not os.path.isdir(DIR):
        os.makedirs(DIR)
    DIR = DIR + os.sep


def checkConfig():
    print "[+] Checking config",
    if mu_username == "" or mu_password == "":
        print "\t\t\t\t[ERROR]\n    Please check your credentials for Megaupload.com"
    elif er_username == "" or er_password == "":
        print "\t\t\t\t[ERROR]\n    Please check your credentials for EasyRewards.fr"
    elif USER_AGENT == "":
        print "\t\t\t\t[ERROR]\n    Please check your customized user-agent"
    else:
        print "\t\t\t\t[OK]"
        if COOKIE_MU_HAPPYHOUR == "":
            print "    HappyHour cookie is empty"
            if raw_input('    Do you want to import it from Firefox [o/n] ? ') == "o":
                importCookieHH()
        return True
    return False


def start():
    day = DIR + datetime.date.today().strftime("%y%m%d")
    if connectToEr() and connectToMu():
        if AUTO or VALIDKEY:
            keyfile = keyIsAvailable()
            if keyfile != None:
                validKey(getKey(keyfile))
        if AUTO or CHOOSEFILE:
            if needToChooseFile():
                filename = getGeneratedFile()
                if filename != None:
                    link = uploadFile(filename)
                    if link != None:
                        os.remove(DIR + filename)
                        if addFileToManager(link, filename):
                            chooseFile(link)
        if AUTO or DOWNLOADLIST:
            if listIsAvailable():
                downloadList(downloadFilelist())
            elif os.path.isfile(DIR + day + '.txt'):
                downloadList(DIR + day + '.txt')
        if not AUTO and DOWNLOADUNAV:
            if os.path.isfile(DIR + day + '.unavailable.txt'):
                downloadList(DIR + day + '.unavailable.txt')
        logoutToMu()
        logoutToEr()
    if OFF:
        shutdown()


def startTest():
    print "=== Tests"


def usage():
    print "Usage : " + os.path.basename(sys.argv[0]) + " [Options]"
    print ""
    print "Options:"
    print "    -h|--help              : Show help"
    print "    -d|--dir directory     : Choose working directory"
    print "    -s|--shutdown          : Shutdown computer at the end"
    print "    --validkey             : Only get and valid the key"
    print "    --choosefile           : Only upload and choose file"
    print "    --downloadlist         : Only get and download/redownload list of files"
    print "    --downloadunav         : Only download/redownload unavailable files"
    print ""
    print "Example : " + os.path.basename(sys.argv[0]) + " -d Easyrewards --validkey --choosefile"
    sys.exit(0)

if __name__ == '__main__':
    options()
    loadConfig()
    if TEST:
        startTest()
    else:
        if checkConfig():
            start()
