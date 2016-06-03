import urlparse
import re

def get_root_domain(url):
	tup = urlparse.urlparse(url)
	netloc = tup.netloc 
	p1 = netloc.rfind('.')
	p2 = netloc.rfind('.',0,p1)
	rootDomain = ''
	if p2 == -1:
		rootDomain = netloc
	else:
		rootDomain = netloc[p2+1:]
	return rootDomain
url = 'http://.com'
rst = get_root_domain(url)
print rst





