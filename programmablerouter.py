import requests
import sys

from bs4 import BeautifulSoup
from bs4.element import Tag

session = requests.session()

class ProgrammableRouter:

    def __init__(self, router, username=None, password=None):
        self.router = router
        self.username = username
        self.password = password

    def login(self):
        d = {'usernamefld': self.username, 'passwordfld': self.password, 'login':''}

        req = session.get("%s/index.php" % self.router)
        if "Login to pfSense" in req.text:
            soup = BeautifulSoup(req.text, 'html.parser')
            csrf_tag = soup.find_all('input', attrs={'name':'__csrf_magic', 'type': 'hidden'}, recursive=True)[0]#(type='input')#, name="__csrf_magic")
            csrf_magic = csrf_tag.get('value')

            d['__csrf_magic'] = csrf_magic

        req = session.post("%s/index.php" % self.router, data=d)

        if 'Login to pfSense' not in req.text:
            sysinfo = {}

            soup = BeautifulSoup(req.text, 'html.parser')
            divtag = soup.find('div', id='widget-system_information_panel-body', recursive=True)
            for child in divtag.find_all('tr'):
                #tr
                key = ""
                val = ""
                for element in child.children:
                    if element.name == 'th':
                        key = element.get_text().strip().replace("\n","").replace("\t"," ")
                    elif element.name == 'td':
                        val = element.get_text().strip().replace("\n","").replace("\t"," ")

                sysinfo[key] = val

            self.sysinfo = sysinfo

    def get_fw_aliases(self):
        req = session.get("%s/firewall_aliases.php?tab=all" % self.router)
        soup = BeautifulSoup(req.text, 'html.parser')
        tbody_results = soup.find('tbody', recursive=True)
        aliases = []
        for tr in tbody_results.children:
            if tr.name == 'tr':
                tags = [x for x in tr.children if x.name == 'td']
                print tags
                if len(tags) > 2:
                    alias_id = list(tags[3].children)[1].get('href').split("=")[1]
                    alias_name = tags[0].get_text().strip()
                    alias_ips = tags[1].get_text().strip().split(", ")
                    fw = {'id': alias_id, 'name': alias_name, 'value': alias_ips}
                    aliases.append(fw)
        return aliases

    def save_fw_alias(self, id, name, value):
        data = {'name': name, 'id': id, 'save': 'Save', 'tab': 'all', 'type': 'host'}

        iter_num = 0
        for ip in value:
            if ip.strip() != "":
                data['address%s' % iter_num] = ip
                data['detail%s' % iter_num] = ""  # todo - preserve this value
                iter_num += 1

        print data
        req = session.post("%s/firewall_aliases.php?tab=all" % self.router, data=data)
        print req.status_code

        # apply the changes
        apply_changes = {'apply': 'Apply Changes'}
        req = session.post("%s/firewall_aliases.php?tab=all" % self.router, data=apply_changes)
        print req.status_code