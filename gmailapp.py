import imaplib, re, json, email

class pygmail:
	def __init__(self, username, password):
		self.IMAP_SERVER = 'imap.gmail.com'
		self.IMAP_PORT = 993
		self.M = None
		self.response = None
		self.username = username
		self. password = password
		self.folders = []
		self.foldersInfo = {}
		self.emailList = []
		self.emailListInfo = {}
	
	def login(self):
		self.M = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
		rc, self.response = self.M.login(self.username, self.password)
		return rc
	
	def logout(self):
		self.M.logout()

	def get_mailboxes(self):
		rc, self.response = self.M.list()
		self.mailboxes = []
		for item in self.response:
			item = item.split()[-2:]
			if item[0] == '"/"':
				item = item[1]
			item = ''.join(item)
			self.mailboxes.append(item)
		return rc

	def rename_mailbox(self, oldmailbox, newmailbox):
		rc, self.response = self.M.rename(oldmailbox, newmailbox)
  		return rc
 
	def create_mailbox(self, mailbox):
		rc, self.response = self.M.create(mailbox)
		return rc
 
	def delete_mailbox(self, mailbox):
		rc, self.response = self.M.delete(mailbox)
  		return rc

	def get_mail_count(self, folder):
		rc, count = self.M.select(folder)
		return count[0]

	def get_unread_count(self, folder):
		rc, self.response = self.M.status(folder, "(UNSEEN)")
		unreadCount = re.search("UNSEEN (\d+)", self.response[0]).group(1)
		return unreadCount

	def get_imap_quota(self):
		quotaStr = self.M.getquotaroot("Inbox")[1][1][0]
		r = re.compile('\d+').findall(quotaStr)
		if r == []:
			r.append(0)
			r.append(0)
		return float(r[1])/1024, float(r[0])/1024

	def get_mails_from(self, uid, folder):
		status, count = self.M.select(folder, readonly=1)
		status, response = self.M.search(None, 'FROM', uid)
		email_ids = [e_id for e_id in response[0].split()]
		return email_ids

	def get_mail_from_id(self, id):
		status, response = self.M.fetch(id, '(body[header.fields (subject)])')
		return response

	def search(self, folder= 'Inbox'):
		self.M.select(folder)
		result, data = self.M.search(None, 'ALL')
		ids = data[0]
		id_list = ids.split()
		for i in id_list:
			typ, data = self.M.fetch(i,'(RFC822)')
			for response_part in data:
				if isinstance(response_part, tuple):
					msg = email.message_from_string(response_part[1])
					sender = msg['from'].split()[-1]
					if self.username not in sender:
						self.emailList.append(sender)
		for mail in self.emailList:
			if mail not in self.emailListInfo:
				self.emailListInfo[mail] = 1
			else:
				self.emailListInfo[mail] += 1
		createSenderInfoJSON(self.emailListInfo) 

def main():
	username = raw_input('Please enter your username: \n')
	if 'gmail.com' not in username:
		username = username + '@' + 'gmail.com'
	password = raw_input('Enter your password: \n')
	g = pygmail(username, password)
	g.login()
	g.get_mailboxes()
	print "Following folders are present:"
	for item in g.mailboxes:
		g.folders.append(item)
		print "Folders -> " + str(item) 
	for folder in g.folders:
		#hack introduced to remove folder names like GMAIL/TRASH, GMAIL/SPAM etc...
		if 'Gmail' in folder:
			continue
		else:
			g.foldersInfo[folder] = {"Total Mails": str(g.get_mail_count(folder)), "Unread Mails": str(g.get_unread_count(folder))}
	#print g.foldersInfo
	createFolderInfoJSON(g.foldersInfo)
	g.search()
	g.logout()

def createFolderInfoJSON(info):
	with open('GmailFolderData.json', 'wb') as fp:
    		json.dump(info, fp)

def createSenderInfoJSON(info):
	with open('GmailSenderData.json', 'wb') as fp1:
		json.dump(info, fp1)

main()
