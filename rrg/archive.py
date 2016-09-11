import os
import re
from tabulate import tabulate
import xml.etree.ElementTree as ET


pat = '[0-9]{5}\.[xX][Mm][Ll]$'
def employees(args):
    ids = []
    firsts = []
    lasts = []
    i = 1
    for root, dirs, files in os.walk(args.datadir):
        if root == args.datadir:
            print('root="%s"' % root)
            for f in files:
                if re.search(pat, f):
                    fullpath = os.path.join(root, f)
                    doc = ET.parse(fullpath).getroot()
                    firstname = doc.findall('firstname')[0].text
                    lastname = doc.findall('lastname')[0].text
                    ids.append(str(i))
                    firsts.append(firstname)
                    lasts.append(lastname)
                    i += 1
    res_dict_transposed = {
        'id': [i for i in ids],
        'first': [i for i in firsts],
        'last': [i for i in lasts],
    }
    print(tabulate(res_dict_transposed, headers='keys', tablefmt='plain'))


def employee(args):
    i = 1
    for root, dirs, files in os.walk(args.datadir):
        if root == args.datadir:
            print('root="%s"' % root)
            for f in files:

                if re.search(pat, f):
                    if i == args.id:
                        fullpath = os.path.join(root, f)
                        doc = ET.parse(fullpath).getroot()
                        firstname = doc.findall('firstname')[0].text
                        lastname = doc.findall('lastname')[0].text
                        print ('id="%s", first="%s", last="%s"' % (i, firstname, lastname))
                    i += 1
