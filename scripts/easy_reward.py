import urllib, mimetypes, mimetools, urllib2, cookielib, sys, time, datetime
import getopt, os, re, random

# Megaupload.com account

mu_username = ""
mu_password = ""

# EasyRewards.fr account

er_username = ""
er_password = ""

# Config

dir = "EasyRewards"
CHROME = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30'

# Global vars

mu_cookie = cookielib.MozillaCookieJar('tasks.cookies')
er_cookie = cookielib.MozillaCookieJar('tasks.cookies')
mu_opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
	urllib2.HTTPHandler(), urllib2.HTTPCookieProcessor(mu_cookie))
er_opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
	urllib2.HTTPHandler(), urllib2.HTTPCookieProcessor(er_cookie))
	
# Utils
	
def pad(s, w):
	return " "*(w-len(s)) + s
	
def toFile(s, name):
	localFile = open(name, 'w')
	localFile.write(s)
	localFile.close()	
	
################################################################################	

def downloadList():    
	print "[+] Reading filelist"
	f = open(dir + time.strftime("%y%m%d") + ".txt", 'r')
	list = f.readlines()
	f.close()	
	
	list = [elem.strip() for elem in list if len(elem.strip()) > 0]
	list = [elem for elem in list if elem.startswith("http://www.megaupload.com")]
	print "    " + str(len(list)) + " file(s) found"
	
	downdir = os.path.normpath(dir + time.strftime("%y%m%d"))
	if not os.path.isdir(downdir):
		os.makedirs(downdir)
	
	for i in range(len(list)):
		print pad(str(i+1), len(str(len(list)))) + "/" + str(len(list)) + " : " + list[i]
		downloadFile(list[i])
		
def downloadFile(link):
	response = mu_opener.open(link)
	source = response.read()
	premium = True
	start = source.find('<div class="down_ad_pad1">')
	if start == -1:
		premium = False
		start = source.find('<div class="down_butt_bg3">')
		if start == -1:
			print "           File is not available !"
			return False
			
	realLink = source[source.find("http", start):source.find('"', source.find("http", start))]
	
	if not premium:
		timetowait = source[source.find("count=", start)+6:source.find(';', source.find("count=", start))]
		print "           Waiting " + timetowait + " secs ..."
		time.sleep(int(timetowait) + 1)
		
	filename = realLink.split('/')[-1]
	print '           Downloading ' + filename
	try:
		response = mu_opener.open(realLink)
		localFile = open(dir + time.strftime("%y%m%d") + os.sep + filename, 'w')
		localFile.write(response.read())
		localFile.close()
		return True
	except urllib2.URLError:
		print "        Error :("
		localFile.close()
		if os.path.exists(dir + filename):
			os.remove(dir + filename)
		return False
	
def encode_multipart_formdata_for_file(filename):
	BOUNDARY = mimetools.choose_boundary()
	CRLF = '\r\n'
	CHARSET = [chr(i) for i in ([20] + range(65, 91) + range(97, 123))]
	L = []

	L.append('--' + BOUNDARY)
	L.append('Content-Disposition: form-data; name="multimessage_0"')
	L.append('')
	L.append(''.join([random.choice(CHARSET) for i in range(random.randint(10, 30))]))
		
	L.append('--' + BOUNDARY)
	L.append('Content-Disposition: form-data; name="multifile_0"; filename="%s"' % os.path.basename(filename))
	L.append('Content-Type: application/octet-stream')
	L.append('')
	tmp = open(dir + filename, 'r')
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
	print "[+] Uploading \""+filename+"\""
	response = mu_opener.open("http://www.megaupload.com/multiupload/").read()
	uploadlink = re.compile("(http://www\d+.megaupload\.com/upload_done\.php\?UPLOAD_IDENTIFIER=\d+)").search(response)
	if uploadlink:
		uploadlink = uploadlink.group(0)
		content_type, body = encode_multipart_formdata_for_file(filename)
		headers = {'Content-Type': content_type, 'Content-Length': str(len(body))}
		response = urllib2.urlopen(urllib2.Request(uploadlink, body, headers))
		if response.code == 200:
			link = re.compile("(http://www\.megaupload\.com/\?d=[0-9A-Z]+)").search(response.read())
			if link:
				print "    Link is : " + link.group(0)
				return link.group(0)
	print "    Error :("
	return None
	
def connectToMu():
	print "[+] Logging in Megaupload.com"
	login_data = urllib.urlencode({'username' : mu_username, 'password' : mu_password, 'login' : 1, 'redir' : 1})
	response = mu_opener.open("http://www.megaupload.com/?c=login", login_data)
	if response.code == 200:
		for cookie in mu_cookie:
			if cookie.name == "user":
				print "    Succefully logged"
				return True
	print "    Error : Check your username and password for Megaupload.com"
	return False
	
def logoutToMu():
	print "[+] Logging out Megaupload.com"
	logout_data = urllib.urlencode({'logout' : 1})
	mu_opener.open("http://www.megaupload.com/?login=1", logout_data)
	mu_cookie.clear_session_cookies()	
	
################################################################################	
	
def connectToEr():
	print "[+] Logging in EasyRewards.fr"
	login_data = urllib.urlencode({'nom' : er_username, 'pass' : er_password, 'seconnecter' : 'Se connecter'})
	req = urllib2.Request("http://www.easyrewards.fr/connexion.php", login_data)
	req.add_header('User-agent', CHROME)
	response = er_opener.open(req)
	if response.code == 200:
		if response.read().find('URL=suivi.php') != -1:
			print "    Succefully logged"
			return True
	print "    Error : Check your username and password for EasyRewards.fr"
	return False
	
def keyIsAvailable():
	print "[+] Checking if key is needed"
	req = urllib2.Request("http://www.easyrewards.fr/suivi.php")
	req.add_header('User-agent', CHROME)
	response = er_opener.open(req).read()
	keyword = response.find('Vous trouverez la')
	if keyword != -1:
		keyfile = response[response.find('"', keyword)+1:response.find('".', keyword)]
		print '    Key can be found in "' + keyfile + '"'
		return 	keyfile
	else:
		print '    Nothing to do'
		return None
	
def getKey(f):
	d = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%y%m%d")
	key = None
	try:
		localFile = open(dir + d + os.sep + f, 'r')
		key = localFile.read()
		localFile.close()
		key = key[key.find('"', key.find('activation est'))+2:key.find('".', key.find('activation est'))-1]
		print '    Key is "' + key + '"'
	except IOError:
		print '    Unable to read "' + f + '"'
	return key

def addFileToManager(link):
	print "[+] Checking if key is needed"
	data = urllib.urlencode({'url' : link, 'btajoutfichier' : 'Valider'})
	req = urllib2.Request("http://www.easyrewards.fr/gestion.php?gestionnaire", data)
	req.add_header('User-agent', CHROME)
	response = er_opener.open(req).read()
	return response.find(link) != -1
	
def validKey(k):
	if k != None:
		data = urllib.urlencode({'cleactivation' : k, 'btvalidationcleactivation' : 'Valider la clé d\'activation'})
		req = urllib2.Request("http://www.easyrewards.fr/suivi.php", data)
		req.add_header('User-agent', CHROME)
		response = er_opener.open(req).read()
		if response.find('licitation'):
			print "    Key has been validated"
			return True
	print "    Key has not been validated"
	return False

	
def listIsAvailable():
	print "[+] Checking if a new filelist is available"
	req = urllib2.Request("http://www.easyrewards.fr/suivi.php")
	req.add_header('User-agent', CHROME)
	response = er_opener.open(req).read()
	if response.find('Merci, vous aurez donc') == -1:
		return response.find('chargez la liste des fichiers du jour') != -1
	return False
	
def downloadFilelist():
	print "    Downloading new filelist"
	filename = time.strftime("%y%m%d") + ".txt"
	req = urllib2.Request("http://www.easyrewards.fr/dl.php")
	req.add_header('User-agent', CHROME)
	response = er_opener.open(req)
	localFile = open(dir + filename, 'w')
	localFile.write(response.read())
	localFile.close()

def needToChooseFile():
	print "[+] Checking if a new file is needed"
	req = urllib2.Request("http://www.easyrewards.fr/suivi.php")
	req.add_header('User-agent', CHROME)
	response = er_opener.open(req).read()
	return response.find('Merci de selectionner le fichier que vous souhaitez poster') != -1
	
def getGeneratedFile():
	print "[+] Downloading new generated file"
	req = urllib2.Request("http://www.easyrewards.fr/generateur.php")
	req.add_header('User-agent', CHROME)
	response = er_opener.open(req)
	localName = response.info()['Content-Disposition'].split('filename=')[1]
	if localName[0] == '"' or localName[0] == "'":
		localName = localName[1:-1]
	localFile = open(dir + localName, 'w')
	localFile.write(response.read())
	localFile.close()
	print "    Name is \""+localName+"\""
	return localName
	
def chooseFile(link):
	print "[+] Choosing "+link+" as next file"
	data = urllib.urlencode({'url' : link, 'btfchiermu' : ' Valider '})
	req = urllib2.Request("http://www.easyrewards.fr/suivi.php", data)
	req.add_header('User-agent', CHROME)
	response = er_opener.open(req).read()
	return response.find('Merci de selectionner le fichier que vous souhaitez poster') == -1
	
def logoutToEr():
	print "[+] Logging out EasyRewards.fr"
	req = urllib2.Request("http://www.easyrewards.fr/deconnexion.php")
	req.add_header('User-agent', CHROME)
	er_opener.open(req)	
	er_cookie.clear_session_cookies()

################################################################################	
	
def options():
	global username, password, dir
	try:
		opts, args = getopt.getopt(sys.argv[1:], "d:h", ["dir", "help"])
	except getopt.error, msg:
		print msg
		usage()

	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
		elif o in ("-d", "--dir"):
			dir = a
			
	dir = os.path.normpath(dir)
	if not os.path.isdir(dir):
		os.makedirs(dir)
	dir = dir + os.sep
	
def start():
	if connectToEr() and connectToMu():
		keyfile = keyIsAvailable()
		if keyfile != None:
			validKey(getKey(keyfile))
		if needToChooseFile():
			file = getGeneratedFile()
			link = uploadFile(file)
			os.remove(dir + file)
			if addFileToManager(link):
				chooseFile(link)
		if listIsAvailable():
			downloadFilelist()
			downloadList()
		logoutToMu()
		logoutToEr()
			
def usage():
	print "Usage : " + os.path.basename(sys.argv[0]) + "[-d dir]"
	sys.exit(0)
			
if __name__ == '__main__':
	options()
	start()
	