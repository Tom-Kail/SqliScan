# coding=utf-8
import Queue
import sys
import webbrowser
import re
import request
import bloomFilter
import urlparse
import formParse
import config.config
import scripts.sqli.bsqli_response_diff as bsqli
from bs4 import BeautifulSoup
from posixpath import normpath

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
    #seed = 'http://192.168.42.138/' # web for pentest
    
    #seed = Request(base='http://192.168.42.131/dvwa/index.php',url='http://192.168.42.131/dvwa/index.php',method='get')
    seed = request.Request(base='http://192.168.42.133',url='http://192.168.42.133/',query={},method='get')
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
        req._cookies = cookie
        # test sqli vuln
    
        print 'req._BFUrl: ',req._BFUrl,' ',req._method,' ', req._source
        #print 'Url: ',req._url
        count += 1
        html = ''
        try:
            rsp = request.sendRequest(req)
            if rsp != None:
                html = rsp.content
        except Exception as err:
            print '[Spider Error]: ',err,' Url: ',req._url
   
        try:
            rsp = bsqli.start(req)
            if rsp != None:
                print "Find Vuln!!"
        except Exception as err:
            print '[Check Vuln Error]: ',err 
            
        # parse form in response content
        soup = BeautifulSoup(html,'lxml')
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
            tmpReq = request.Request(req._url,url,'get')
            netlocTmp = urlparse.urlparse(tmpReq._url).netloc
            if netlocTmp == netloc:
                reqs.append(request.Request(base=req._url,url=url,method='get'))
        
        # prase url by bloomFilter and treeFilter ?++?
        for x in reqs:
            if not bf.exist(x._BFUrl):
                bf.insert(x._BFUrl)
                q.put(x)
        
    print "Number of url:",count

            
