# coding=utf-8

import sys
import re
import request
import urlparse
import formParse
import config.config as config
from bs4 import BeautifulSoup
NotCrawlList=(
    'logout',
    'exit',
    'security',
    'phpids',
    'sigout',
   'logoff','signoff','quit','bye-bye','clearuser','invalidate','注销','退出','再见','清除用户','无效'
    )

def not_crawl(req):
    for i in NotCrawlList:
        if req._url.find(i)!=-1:
            return True
        for j in req._query:
            if j.find(i)!=-1:
                return True
            if req._query[j].find(i)!=-1:
                return True
    return False

def crawl(req):
    # begin crawler
    tup = urlparse.urlparse(req._url)
    # test sqli vuln
    #print '\nreq._BFUrl: ',req._BFUrl,' ',req._method,' ', req._source
    html = ''
    try:
        if req._source == 'regex':
            rsp = request.sendRequest(req)
            if rsp != None:
                html = rsp.content
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
            
