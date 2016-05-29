# coding=utf8
from bs4 import BeautifulSoup
import Levenshtein
import config.config as config
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def getUnicode(s):
	if isinstance(s,str):
		return s.decode('ascii')
	else:
		return s

def compare(strA, strB):

	a = getUnicode(strA)
	b = getUnicode(strB)
	
	try :
		ratio = Levenshtein.ratio(a,b)
		#print ratio
		if ratio >= config.conf['PageSimilarity']:
			return True
		else:
			return False
	except Exception as err:
		print err
		
def genTagList(html,tagList):
	soup = BeautifulSoup(html,'lxml')
	for tag in soup.descendants:
		if tag.name !=None:
			if tag.name == 'a':
				href = tag.get('href')
				tagList.append('<'+tag.name+('' if href==None else ' ' + href) +'>')
			elif tag.name=='form':
				action = tag.get('action')
				tagList.append('<'+tag.name+('' if action==None else ' ' + action) +'>')
			elif tag.name=='input':
				option = tag.get('name')
				tagList.append('<'+tag.name+('' if option==None else ' ' + option) +'>')
			else:
				tagList.append('<'+tag.name+'>')

def genTagStr(html):
	tagList = []
	genTagList(html,tagList)
	return ''.join(tagList)
