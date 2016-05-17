# coding=utf-8

import sys
import re
import request
import urlparse
import chardet
import formParse
from config.config import conf
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

NotCrawlList=(
    'logout',
    'exit',
    'security',
    'phpids',
    'sigout','.js','.css',
   'logoff','signoff','quit','bye-bye','clearuser','invalidate','注销','退出','再见','清除用户','无效'
    )

def toUTF8(s):
    return s
    encoding = chardet.detect(s)
    if encoding['encoding'] == 'GB2312':
        s = s.decode('GB2312','ignore').encode('utf-8')
    elif encoding['encoding'] == 'GBK':
        s = s.decode('gbk','ignore').encode('utf-8')
    return s

def not_crawl(req):
    for i in NotCrawlList:
        try:
            if req._url.find(i)!=-1:
                return True
            for j in req._query:
                if j.find(i)!=-1:
                    return True
                if req._query[j].find(i)!=-1:
                    return True
        except Exception as err:
            return False
    return False

def crawl(req):
    # begin crawler
    req._timeout = conf['connTimeout'] 
    tup = urlparse.urlparse(req._url)
    # test sqli vuln
    #print '\nreq._BFUrl: ',req._BFUrl,' ',req._method,' ', req._source
    html = ''
    try:
        if req._source == 'regex':
            rsp = request.sendRequest(req)
            if rsp != None:
                html = toUTF8(rsp.content)
    except Exception as err:
        print '[Spider Error]: ',err,' Url: ',req._url

    # parse form in response content
    soup = BeautifulSoup(html)
    formReqs = []
    #formPat = re.compile(r'<form[\S\s]*?</form>')
    #forms = formPat.findall(html)
    #print forms
    forms = []
    try:
        forms = soup.find_all(name='form')
    except Exception as err:
        print err
    
    #forms = soup.find_all(name='form')
    for child in forms:
        #print child:wq
        #print child
        #tmp = BeautifulSoup(child)
        tmpForm = formParse.Form(req._url,str(child))
        tmpReq = tmpForm.getReq()
        if not not_crawl(tmpReq):
            formReqs.append(tmpReq)

    #print 'form urls :',formReqs:
    
    hrefPat = re.compile(r'href="([\S]{5,})"')
    srcPat = re.compile(r'src="([\S]{5,})"')
    urls = hrefPat.findall(html)
    urls.extend(srcPat.findall(html))
    reqs =[]
    reqs.extend(formReqs)

    # only crawl url with the same netloc
    for url in urls:

        tmpReq = request.Request(req._url,url,'get')
        if  not_crawl(tmpReq):
            continue
        netlocTmp = urlparse.urlparse(tmpReq._url).netloc
        if netlocTmp == tup.netloc:
            reqs.append(request.Request(base=req._url,url=url,method='get'))
    
    return reqs
            
