# coding=utf-8

import sys
import re
import request
import urlparse
import formParse
import config.config as config
import scripts.sqli.bsqli_response_diff as bsqlitf
import scripts.sqli.bsqli_time_delay as bsqlitd
import scripts.sqli.sqli as sqli
from bs4 import BeautifulSoup


def crawl(req):
    # begin crawler
    tup = urlparse.urlparse(req._url)
    # test sqli vuln
    print '\nreq._BFUrl: ',req._BFUrl,' ',req._method,' ', req._source
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
        formReqs.append(tmpForm.getReq())

    #print 'form urls :',formReqs:
    
    hrefPat = re.compile(r'href="([\S]{5,})"')
    srcPat = re.compile(r'src="([\S]{5,})"')
    urls = hrefPat.findall(html)
    urls.extend(srcPat.findall(html))
    reqs =[]
    reqs.extend(formReqs)

    # only crawl url with the same netloc
    for url in urls:
        if url.find('logout') != -1:
            continue

        tmpReq = request.Request(req._url,url,'get')
        netlocTmp = urlparse.urlparse(tmpReq._url).netloc
        if netlocTmp == tup.netloc:
            reqs.append(request.Request(base=req._url,url=url,method='get'))
    
    return reqs
            
