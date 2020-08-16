#!/usr/bin/python

import csv
import os
import sys

import MySQLdb as sql
import xlrd

host, user, password, dbName = "localhost", "root", "", "dump"

con, cur = None, None

cmd = None


class Options:
    type = None
    file = None
    email = None
    firstname = None
    lastname = None
    ip = None
    username = None
    website = None


def help():
    print("Usage: " + os.path.basename(sys.argv[0]) + ' command [options]')
    print()
    print("Command list:")
    print("    h, -h, --help, /h            : Show help")
    print("    i                            : Show some stats")
    print("      --website xxx")
    print("    ls                           : Show pwned websites")
    print("    l                            : Generate passwords list")
    print("    lu                           : Generate uncracked hashes list")
    print("      --website xxx")
    print("    u                            : Update database with POT file")
    print("      --in FILE")
    print("    a                            : Add pwned users to the database")
    print("      --in FILE")
    print("      --type (txt|csv|xls|havij)")
    print("    f                            : Find pwned users (support * and ?)")
    print("      --username xxx")
    print("      --firstname xxx")
    print("      --lastname xxx")
    print("      --email xxx")
    print("      --ip xxx")
    print("      --website xxx")
    print()
    sys.exit(0)


def connect():
    global con
    try:
        con = sql.connect(host, user, password, dbName)
    except Exception as e:
        print(e[1])
        sys.exit(0)


def disconnect():
    if con is not None:
        con.commit()
        con.close()


def stats():
    global cur
    cur = con.cursor()
    print("[+] Info about", end=' ')

    if opt_website:
        print(opt_website)
    else:
        print("database")

    if opt_website:
        cur.execute('SELECT COUNT(*), 1 FROM users WHERE website LIKE \'' + opt_website + '\';')
    else:
        cur.execute('SELECT COUNT(*),COUNT(DISTINCT website) FROM users;')
    val = cur.fetchone()
    if not opt_website:
        print("%20s : %d" % ("Sites", val[1]))
    print("%20s : %d" % ("Users", val[0]))
    userCount = int(val[0])

    if userCount > 0:

        if opt_website:
            cur.execute(
                'SELECT COUNT(DISTINCT clearpassword) FROM users WHERE LENGTH(clearpassword)>0 AND website LIKE \'' + opt_website + '\';')
        else:
            cur.execute('SELECT COUNT(DISTINCT clearpassword) FROM users WHERE LENGTH(clearpassword)>0;')
        val = cur.fetchone()
        print("%20s : %d" % ("Passwords", val[0]))
        passCount = int(val[0])

        if opt_website:
            cur.execute(
                'SELECT COUNT(DISTINCT hashedpassword) FROM users WHERE LENGTH(hashedpassword)>0 AND website LIKE \'' + opt_website + '\';')
        else:
            cur.execute('SELECT COUNT(DISTINCT hashedpassword) FROM users WHERE LENGTH(hashedpassword)>0;')
        val = cur.fetchone()
        print("%20s : %d" % ("Hashes", val[0]))
        hashCount = int(val[0]) + 0.00001

        if opt_website:
            cur.execute(
                'SELECT COUNT(DISTINCT hashedpassword) FROM users WHERE LENGTH(clearpassword)=0 AND LENGTH(hashedpassword)>0 AND website LIKE \'' + opt_website + '\';')
        else:
            cur.execute(
                'SELECT COUNT(DISTINCT hashedpassword) FROM users WHERE LENGTH(clearpassword)=0 AND LENGTH(hashedpassword)>0 ;')
        val = cur.fetchone()
        print("%20s : %d (%4.2f" % ("Uncracked", val[0], 100.0 * int(val[0]) / hashCount) + "%)")

        if passCount > 0:
            print()
            print("    Ordered password length:")

            if opt_website:
                cur.execute(
                    'SELECT LENGTH(clearpassword), COUNT(*) FROM users WHERE website LIKE \'' + opt_website + '\' GROUP BY LENGTH(clearpassword) ORDER BY LENGTH(clearpassword) ASC;')
            else:
                cur.execute(
                    'SELECT LENGTH(clearpassword), COUNT(*) FROM users GROUP BY LENGTH(clearpassword) ORDER BY LENGTH(clearpassword) ASC;')
            rows = cur.fetchall()
            for val in rows:
                if (val[0] != 0):
                    print("%20s : %7s (%4.2f" % (val[0], val[1], 100.0 * int(val[1]) / userCount) + "%)")

            print()
            print("    Top50 password:")

            if opt_website:
                cur.execute(
                    'SELECT clearpassword, COUNT(*) as Total FROM users WHERE LENGTH(clearpassword)>0 AND website LIKE \'' + opt_website + '\' GROUP BY clearpassword ORDER BY Total DESC LIMIT 50;')
            else:
                cur.execute(
                    'SELECT clearpassword, COUNT(*) as Total FROM users WHERE LENGTH(clearpassword)>0 GROUP BY clearpassword ORDER BY Total DESC LIMIT 50;')
            rows = cur.fetchall()
            for val in rows:
                print("%20s : %4.2f" % (val[0], 100.0 * int(val[1]) / userCount) + "%")

        print()
        print("    Top10 domain:")

        if opt_website:
            cur.execute(
                'SELECT SUBSTRING_INDEX(email, "@", -1) as Domain, count(*) as Total FROM users WHERE website LIKE \'' + opt_website + '\' GROUP BY Domain ORDER BY Total DESC LIMIT 10;')
        else:
            cur.execute(
                'SELECT SUBSTRING_INDEX(email, "@", -1) as Domain, count(*) as Total FROM users GROUP BY Domain ORDER BY Total DESC LIMIT 10;')
        rows = cur.fetchall()
        for val in rows:
            print("%20s : %4.2f" % (val[0], 100.0 * int(val[1]) / userCount) + "%")

        print()
        print("    Interesting domains:")

        if opt_website:
            cur.execute(
                'SELECT SUBSTRING_INDEX(email, ".", -1) as Tld, count(*) as Total FROM users WHERE SUBSTRING_INDEX(email, ".", -1) IN (\'edu\', \'gov\', \'mil\') AND website LIKE \'' + opt_website + '\' GROUP BY Tld ORDER BY Total')
        else:
            cur.execute(
                'SELECT SUBSTRING_INDEX(email, ".", -1) as Tld, count(*) as Total FROM users WHERE SUBSTRING_INDEX(email, ".", -1) IN (\'edu\', \'gov\', \'mil\') GROUP BY Tld ORDER BY Total')
        rows = cur.fetchall()
        for val in rows:
            print("%20s : %d" % (val[0], val[1]))

    print()
    cur.close()


def pad(s, size):
    return s + " " * (size - len(s))


def listSites():
    global cur
    cur = con.cursor()

    print("[+] Listing pwned websites")

    cur.execute('SELECT website, COUNT(*) FROM users GROUP BY website;')
    rows = cur.fetchall()
    print("    %d websites found" % (len(rows)))
    print()
    for site in rows:
        print("    %s (%d)" % (site[0], site[1]))

    cur.close()


def findUsers():
    global cur
    cur = con.cursor()
    before = False

    print("[+] Finding pwned users")

    req = 'SELECT * FROM users WHERE '
    if opt_email:
        req += 'email LIKE \'' + con.escape_string(opt_email) + '\' '
        before = True
    if opt_firstname:
        if before:
            req += "AND "
        req += 'firstname LIKE \'' + con.escape_string(opt_firstname) + '\' '
    if opt_lastname:
        if before:
            req += "AND "
        req += 'lastname LIKE \'' + con.escape_string(opt_lastname) + '\' '
    if opt_username:
        if before:
            req += "AND "
        req += 'username LIKE \'' + con.escape_string(opt_username) + '\' '
    if opt_username:
        if before:
            req += "AND "
        req += 'username LIKE \'' + con.escape_string(opt_username) + '\' '
    if opt_website:
        if before:
            req += "AND "
        req += 'website LIKE \'' + con.escape_string(opt_website) + '\' '
    req += ";"

    cur.execute(req)
    rows = cur.fetchall()
    print("    " + str(len(rows)) + " users found")
    print()

    columnsName = ["Username", "Email", "Hash", "Password", "Firstname", "Lastname", "IP Address", "Website"]
    max = len(rows)
    for j in range(max):
        for i in range(len(columnsName)):
            if rows[j][i] != "":
                print("    " + pad(columnsName[i], 11) + ": " + rows[j][i])
        if j < max - 1:
            print("\n    -\n")

    if max > 0:
        print()
    cur.close()


def updateWithPOT():
    global cur

    updateData = []

    print("[+] Reading POT file")
    f = open(opt_file, "r")
    if (f):
        lines = f.readlines()
        f.close()
        for line in lines:
            if len(line) > 0:
                if line[0] == "$":
                    start = line.find("$", 1)
                    end = line.find(":", start)
                    updateData.append([line[end + 1:].strip(), line[start + 1:end]])
                else:
                    updateData.append([line[line.find(":") + 1:].strip(), line[:line.find(":")]])

        print("    " + str(len(updateData)) + " cracked passwords in POT file.")

        print("[+] Updating database")

        affected = 0
        for part in range(0, len(updateData), 10000):
            req = 'UPDATE `users` SET `clearpassword`= CASE `hashedpassword` ' + "\n"
            max = min(part + 10000, len(updateData) + 1)
            for data in updateData[part:max]:
                req += '    WHEN \'' + con.escape_string(data[1]) + '\' THEN \'' + con.escape_string(
                    data[0]) + '\' ' + "\n"
            req += '    ELSE `clearpassword`' + "\n"
            req += '    END' + "\n"
            req += 'WHERE `hashedpassword` IN (' + ','.join(['\'' + h[1] + '\'' for h in updateData[part:max]]) + ');'

            print("        %d to %d" % (part, max - 1))
            cur = con.cursor()
            affected += cur.execute(req)
            cur.close()
        con.commit()

        print("    " + str(affected) + " users updated.")

    else:
        print("[+] Error reading POT file " + os.path.basename(opt_file))
    print()


def generateUncrackedList():
    global cur
    cur = con.cursor()

    print("[+] Generating uncracked hashes list")
    if opt_website:
        cur.execute(
            'SELECT DISTINCT(hashedpassword) FROM users WHERE website LIKE \'' + opt_website + '\' AND LENGTH(clearpassword)=0 AND LENGTH(hashedpassword)>0 ORDER BY hashedpassword ASC;')
    else:
        cur.execute(
            'SELECT DISTINCT(hashedpassword) FROM users WHERE LENGTH(clearpassword)=0 AND LENGTH(hashedpassword)>0 ORDER BY hashedpassword ASC;')
    rows = cur.fetchall()
    f = open("uncracked.txt", "w")
    if (f):
        content = ""
        id = 0
        for val in rows:
            content += "pass" + str(id) + ":" + val[0] + "\n"
            id += 1
        f.write(content)
        f.close()
        print("    " + str(len(rows)) + " passwords written to uncracked.txt")
    else:
        print("[+] Error writing file uncracked.txt !")
    print()
    cur.close()


def generatePassList():
    global cur
    cur = con.cursor()

    print("[+] Generating wordlist, please wait ...")
    cur.execute('SELECT DISTINCT(clearpassword) FROM users WHERE LENGTH(clearpassword)>0 ORDER BY clearpassword ASC;')
    rows = cur.fetchall()
    f = open("wordlist.txt", "w")
    if (f):
        content = ""
        for val in rows:
            content += val[0] + "\n"
        f.write(content)
        f.close()
        print("    " + str(len(rows)) + " passwords written to wordlist.txt")
    else:
        print("[+] Error writing file wordlist.txt !")
    print("")
    cur.close()


def importFromHavij():
    global cur
    dataToAdd = []

    print("[+] Input data from Havij file")
    cols = list(map(int, input("    columns        : ").split(',')))
    colsMan = list(map(int, input("    needed columns : ").split(',')))
    colsNames = "website," + input("    column name    : ")
    site = input("    website        : ")

    print()
    print("[+] Reading file \"" + opt_file + "\"")
    f = open(opt_file, "rb")
    if (f is not None):
        content = f.read()
        pos = content.find("<table border", content.find("<table border", content.find("<table border") + 1) + 1)
        end = content.find("</table>", pos + 1)
        pos = content.find("<tr>", content.find("<tr>", pos + 1) + 1)
        while pos < end and pos != -1:
            end2 = content.find('</tr>', pos + 1)
            pos = content.find("<td ", pos + 1)
            data = []
            while pos != -1 and pos < end2:
                data.append(content[content.find('>', pos + 6) + 1:content.find('<', pos + 10)])
                pos = content.find("<td ", pos + 1)

            toAdd = True
            try:
                for col in colsMan:
                    if len(data[col]) == 0:
                        toAdd = False
                        break
            except:
                toAdd = False

            if toAdd:
                selData = []
                for col in cols:
                    selData.append(data[col])
                dataToAdd.append(selData)

            pos = content.find("<tr>", pos + 1)
        f.close()

        print()
        print("[+] Inserting " + str(len(dataToAdd)) + " new data")

        cur = con.cursor()
        req = 'INSERT INTO users(' + colsNames + ') VALUES(%s' + (',%s' * (len(cols))) + ');'
        affected = cur.executemany(req, dataToAdd)
        cur.close()
        con.commit()

        print("    " + str(affected) + " user(s) inserted")

    else:
        print("[+] Error : Unable to open " + opt_file)
    sys.exit(0)


def importFromXLS():
    global cur
    dataToAdd = []

    print("[+] Input data from XLS file")
    sheet = int(input("    sheet index    : "))
    cols = list(map(int, input("    columns        : ").split(',')))
    colsMan = list(map(int, input("    needed columns : ").split(',')))
    colsNames = "website," + input("    column name    : ")
    site = input("    website        : ")

    print()
    print("[+] Reading file \"" + opt_file + "\"")
    f = xlrd.open_workbook(opt_file)
    if (f is not None):
        sh = f.sheet_by_index(sheet)
        for row in range(sh.nrows):
            toAdd = True
            try:
                for col in colsMan:
                    if len(str(sh.cell(rowx=row, colx=col).value).encode('ascii', 'ignore')) == 0:
                        toAdd = False
                        break
            except:
                toAdd = False

            if toAdd:
                selData = [site]
                for c in cols:
                    selData.append(str(sh.cell(rowx=row, colx=c).value).encode('ascii', 'ignore').strip())
                dataToAdd.append(selData)

        print()
        print("[+] Inserting " + str(len(dataToAdd)) + " new data")

        cur = con.cursor()
        req = 'INSERT INTO users(' + colsNames + ') VALUES(%s' + (',%s' * (len(cols))) + ');'
        affected = cur.executemany(req, dataToAdd)
        cur.close()
        con.commit()

        print("    " + str(affected) + " user(s) inserted")

    else:
        print("[+] Error : Unable to open " + opt_file)
    sys.exit(0)


def importFromCSV():
    global cur
    dataToAdd = []

    print("[+] Input data from CSV file")
    separator = input("    separator (:) : ")
    if separator == "":
        separator = ":"
    cols = list(map(int, input("    columns        : ").split(',')))
    colsMan = list(map(int, input("    needed columns : ").split(',')))
    colsNames = "website," + input("    column name    : ")
    site = input("    website        : ")

    print()
    print("[+] Reading file \"" + opt_file + "\"")
    f = open(opt_file, "rb")
    if (f is not None):
        reader = csv.reader(f, delimiter=separator)
        rownum = 0
        for row in reader:
            if rownum > 0 and len(row) > 0:
                toAdd = True
                for col in colsMan:
                    if len(row[col]) == 0:
                        toAdd = False
                        break

                if toAdd:
                    selData = [site]
                    for c in cols:
                        selData.append(row[c].strip())
                    dataToAdd.append(selData)
            rownum += 1
        f.close()

        print()
        print("[+] Inserting " + str(len(dataToAdd)) + " new data")

        cur = con.cursor()
        req = 'INSERT INTO users(' + colsNames + ') VALUES(%s' + (',%s' * (len(cols))) + ');'
        affected = cur.executemany(req, dataToAdd)
        cur.close()
        con.commit()

        print("    " + str(affected) + " user(s) inserted")

    else:
        print("[+] Error : Unable to open " + opt_file)
    sys.exit(0)


def importFromTxt():
    global cur
    dataToAdd = []

    print("[+] Input data from txt file")
    fromLine = input("    from line (0)  : ")
    if fromLine == "":
        fromLine = 0
    else:
        fromLine = int(fromLine)
    toLine = input("    to line (end)  : ")
    if toLine == "":
        toLine = 0
    else:
        toLine = int(toLine)
    separator = input("    separator (:)  : ")
    if separator == "":
        separator = ":"
    cols = list(map(int, input("    columns        : ").split(',')))
    colsMan = list(map(int, input("    needed columns : ").split(',')))
    colsNames = "website," + input("    column name    : ")
    site = input("    website        : ")

    print()
    print("[+] Reading file \"" + opt_file + "\"")
    f = open(opt_file, "r")
    if (f is not None):
        lines = f.readlines()
        f.close()
        if toLine == 0:
            toLine = len(lines)
        for i in range(fromLine, toLine):
            data = lines[i].split(separator)

            toAdd = True
            try:
                for col in colsMan:
                    if len(data[col]) == 0:
                        toAdd = False
                        break
            except:
                toAdd = False

            if toAdd:
                selData = [site]
                for c in cols:
                    selData.append(data[c].strip())
                dataToAdd.append(selData)

        print("    " + str(len(dataToAdd)) + " users found")
        print()
        print("[+] Inserting new data")

        cur = con.cursor()
        req = 'INSERT INTO users(' + colsNames + ') VALUES(%s' + (',%s' * (len(cols))) + ');'
        affected = cur.executemany(req, dataToAdd)
        cur.close()
        con.commit()

        print("    " + str(affected) + " users inserted")

    else:
        print("[+] Error : Unable to open " + opt_file)
    sys.exit(0)


def readArg(i):
    if i < len(sys.argv) - 1:
        return sys.argv[i + 1]
    else:
        help()


if __name__ == "__main__":
    i = 1
    while i < len(sys.argv):
        opt = sys.argv[i]
        if opt == '-h':
            help()
        elif opt in ("a", "h", "f", "l", "lu", "ls", "-h", "u", "--help", "i"):
            cmd = opt
        elif opt == "--in":
            opt_file = readArg(i)
            i += 1
        elif opt == "--type":
            opt_type = readArg(i)
            i += 1
        elif opt == "--username":
            opt_username = readArg(i).replace("*", "%").replace("?", "_")
            i += 1
        elif opt == "--firstname":
            opt_firstname = readArg(i).replace("*", "%").replace("?", "_")
            i += 1
        elif opt == "--email":
            opt_email = readArg(i).replace("*", "%").replace("?", "_")
            i += 1
        elif opt == "--lastname":
            opt_lastname = readArg(i).replace("*", "%").replace("?", "_")
            i += 1
        elif opt == "--ip":
            opt_ip = readArg(i).replace("*", "%").replace("?", "_")
            i += 1
        elif opt == "--website":
            opt_website = readArg(i).replace("*", "%").replace("?", "_")
            i += 1
        else:
            help()
        i += 1

    if cmd is not None:
        cmd = cmd.lower()
    if opt_type is not None:
        opt_type = opt_type.lower()

    if cmd in ("h", "-h", "--help", "/h"):
        help()
    elif cmd == "i":
        stats()
    elif cmd == "ls":
        listSites()
    elif cmd == "f":
        if opt_email or opt_firstname or opt_lastname or opt_ip or opt_username or opt_website:
            findUsers()
        else:
            help()
    elif cmd == "l":
        generatePassList()
    elif cmd == "lu":
        generateUncrackedList()
    elif cmd == "u":
        if opt_file is not None:
            updateWithPOT()
        else:
            help()
    elif cmd == "a":
        if opt_type == "txt" and opt_file is not None:
            importFromTxt()
        elif opt_type == "csv" and opt_file is not None:
            importFromCSV()
        elif opt_type == "havij" and opt_file is not None:
            importFromHavij()
        elif opt_type == "xls" and opt_file is not None:
            importFromXLS()
        else:
            help()
    else:

        help()

    disconnect()
