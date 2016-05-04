# coding=utf-8
import Queue
import sys
import webbrowser
import re
import requests
import bloomFilter
import urlparse
import formParse
from bs4 import BeautifulSoup
from posixpath import normpath

class Request(object):
    def __init__(self,base,url,method='get',query={},cookie={},source='regex'):
        self._url = myJoin(base,url)
        self._method = method
        self._query = query
        self._cookies = cookie
        self._BFUrl = '' # like ID to identify unique request
        self._source = source
        tup = urlparse.urlparse(self._url)
        
        if self._method == 'get':
            if tup.query != '':
                self._BFUrl = urlparse.urlunparse((tup.scheme,tup.netloc,tup.path,tup.params,'','')) + '?'
                for line in tup.query.strip().split('&'):
                    if line.find('=') == -1:# in case of www.baidu.com/?www.google.com
                        continue
                    #print 'url: ',url,' line:',line,' pos: ',pos
                    name, value = line.strip().split('=',1)
                    self._BFUrl = self._BFUrl + name + '&'
            else:
                self._BFUrl = self._url
        elif self._method == 'post': 
            self._BFUrl = self._BFUrl + url + '?'
            for k in payload.keys():
                self._BFUrl = self._BFUrl + k + '&'
def myJoin(base,url): 
    tup = urlparse.urlparse(url)
    #if tup.netloc == '' and url.find('/') != -1 and len(url) > 0 and url[0] != '/':
    #    url = '/' + url
        #print 'Special Url: ',url
    rst = urlparse.urljoin(base,url)
    #print '   base: ',base,' url: ',url,' rst:',rst
    return rst
'''
    urlTmp = urlparse.urljoin(base,url)
    arr = urlparse.urlparse(urlTmp)
    path = normpath(arr[2])
    
    return urlparse.urlunparse((arr.scheme,arr.netloc,path,arr.params,arr.query,arr.fragment))
'''
def getCompleteUrl(scheme,netloc,path,tmpUrl):
    dirPath = ''
    pos = path.rfind('/')
    if pos != -1:
        dirPath = path[0:pos+1]
    else:
        dirPath = '/'
    tup = urlparse.urlparse(tmpUrl)

    # example:
    #   url: 'example8.php?order=name'
    #   parent url: '192.168.42.138/sqli/example8.php?order=age'
    #   result: '192.168.42.138/sqli/example8.php?order=name'
    if tup.netloc == '':
        if tup.path =='':
            tmpUrl = netloc + path + '?' + tup.query
        elif tup.path[0] == '/':
            tmpUrl = netloc + tmpUrl
        elif tup.path.find('/') == -1:
            tmpUrl = netloc + dirPath + tmpUrl
        else:
            tmpUrl = netloc + '/' + tmpUrl
    if tup.scheme == '':
        tmpUrl = scheme + '://' + tmpUrl
    return tmpUrl

def getCookie(loginUrl):
    if loginUlr == '':
        return ''
    # recording cookie
    try:
        webbrowser.open_new(loginUrl)
    except Exception as err:
        print err
    print 'Please enter "Y" if you finishing recording cookie.'
    while True: 
        finish = raw_input('')
        if finish.lower() == 'y':
            break
        else:
            finish = ''
    # read cookie from cookieFile
    cookieFileName = config.conf['CookieFileName']
    # cookieFileName = '/root/cntzapfile.txt'
    print 'Read cookie from file: ',cookieFileName
    cookiePat = re.compile(r'\bCookie:([\S \t]*)')
    allText = open(cookieFileName).read()
    cookieTmp = cookiePat.findall(allText)
    cookie = {}
    if len(cookieTmp) != 0:
        for line in cookieTmp[0].split(';'):
            name,value = line.strip().split('=',1)
            cookie[name] = value
    print 'cookie is:',cookie
    return cookie
    
    
if __name__ == "__main__":
    if not '/root/WorkSpace/SqliScan/Master/config/' in sys.path:
        sys.path.append('/root/WorkSpace/SqliScan/Master/config/')
    if not 'config' in sys.modules:
        config = __import__('config')
    else:
        eval('import config')
        config = eval('reload(config)')

    #seed = 'http://192.168.42.138/' # web for pentest
    
    #seed = Request(base='http://192.168.42.131/dvwa/index.php',url='http://192.168.42.131/dvwa/index.php',method='get')
    seed = Request(base='http://192.168.42.133',url='http://192.168.42.133',method='get')
    print 'seed url: ',seed._url

    #cookie = getCookie(seed._url)
    cookie ={}
    # begin crawler
    tup = urlparse.urlparse(seed._url)
    netloc = tup.netloc # seed url 
    count = 0
    q = Queue.Queue()
    q.put(seed)
    #q.put(Request('http://192.168.42.131/dvwa/vulnerabilities/sqli/','http://192.168.42.131/dvwa/vulnerabilities/sqli/','get'))
    bf = bloomFilter.BloomFilter(0.001,100000)
    # !!! need deal with seed._url
    bf.insert(seed._url)
    while(not q.empty()):
        req = q.get()
        
        # test sqli vuln
        

        print 'req._BFUrl: ',req._BFUrl,' ',req._method,' ', req._source
        #print 'Url: ',req._url
        count += 1
        html = ''
        try:
            method = req._method.lower()
            if method == 'get':
                r = requests.get(req._url,timeout=1,cookies=cookie)
                html = r.content
            elif method == 'post':
                r = requests.post(req._url,data=req._query,timeout=1,cookies=cookie)
                html = r.content
            else:
                print '[Info] Method '+ method +' not support!'
                pass

        except Exception as err:
            print '[Error]: ',err
        
        # parse form in response content
        soup = BeautifulSoup(html)
        formUrls = []
        #formPat = re.compile(r'<form[\S\s]*?</form>')
        #forms = formPat.findall(r.content)
        forms = []
        try:
            forms = soup.find_all(name='form')
        except Exception as err:
            print err

        #forms = soup.find_all(name='form')
        for child in forms:
            #print child
            #tmp = BeautifulSoup(child)
            tmpForm = formParse.Form(req._url,str(child))
            formUrls.append(tmpForm.getReq())
        #print 'form urls :',formUrls:
        
        hrefPat = re.compile(r'href="([\S]{5,})"')
        srcPat = re.compile(r'src="([\S]{5,})"')
        urls = hrefPat.findall(html)
        urls.extend(srcPat.findall(html))
        reqs =[]
        reqs.extend(formUrls)

        # only crawl url with the same netloc
        for url in urls:
            if url.find('logout') != -1:
                continue
            tmpReq = Request(req._url,url,'get')
            netlocTmp = urlparse.urlparse(tmpReq._url).netloc
            if netlocTmp == netloc:
                reqs.append(Request(req._url,url,'get'))
        
        # prase url by bloomFilter and treeFilter ?++?
        for x in reqs:
            if not bf.exist(x._BFUrl):
                bf.insert(x._BFUrl)
                q.put(x)
        
    print "Number of url:",count

            
