import requests
import sys

from bs4 import BeautifulSoup
from bs4.element import Tag

class ProgrammableRouter:

	def __init__(self, router, username=None, password=None):
		self.router = router
		self.username = username
		self.password = password
		self.session = requests.session()


	def login(self):
		d = {'usernamefld': self.username, 'passwordfld': self.password, 'login':''}

		req = self.session.get("%s/index.php" % self.router)
		if "Login to pfSense" in req.text:
			soup = BeautifulSoup(req.text, 'html.parser')
			csrf_tag = soup.find_all('input', attrs={'name':'__csrf_magic', 'type': 'hidden'}, recursive=True)[0]#(type='input')#, name="__csrf_magic")
			csrf_magic = csrf_tag.get('value')

			d['__csrf_magic'] = csrf_magic

		req = self.session.post("%s/index.php" % self.router, data=d)

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

	def firewall_ip_aliases(self):
		req = self.session.get("%s/firewall_aliases.php?tab=ip" % self.router)
		soup = BeautifulSoup(req.text, 'html.parser')
		tbody_results = soup.find('tbody', recursive=True)
		aliases = []
		for tr in tbody_results.children:
			if tr.name == 'tr':
				tags = [x for x in tr.children if x.name == 'td']
				if len(tags) > 2:
					alias_name = tags[0].get_text().strip()
					alias_ips = tags[1].get_text().strip().split(", ")
					aliases.append({'name': alias_name, 'ips': alias_ips})
		return aliases