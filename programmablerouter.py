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
			#determine version number
			#print req.text

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
				
				#print "%s: %s" % (key, val)
				sysinfo[key] = val

			self.sysinfo = sysinfo