# coding=utf-8

import sys
import re
import request
import urlparse
import chardet
import tagComp as tc
import formParse
import random
import treeFilter as tf
import config.config as config
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

NotCrawlList=(
    'logout','注销','退出','再见','清除用户','无效','exit','bye-bye','clearuser','resetdb','csrf','security','phpids','sigout','.js','.css','logoff','signoff','quit','invalidate'
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


'''
def gen_tree_path(url):
    scheme, host, path, query, fragment = urlparse.urlsplit(url)
    path = '/' if path=='' else path[:path.rfind('/')+1]
    treePath = urlparse.urlunsplit((scheme,host,path,'',''))
    return treePath

def getRandList(max):
    if max < config.conf['SelectNodeNum']:
        return []
    r = []
    for i in range(config.conf['SelectNodeNum']):
        index = random.randint(0,max-1)
        while index  in r:
            index = random.randint(0,max-1)
        r.append(index)
    return r

def checkSimi(tagStr,dir):
    listLen = len(dir['list'])
    randomIndex = getRandList(listLen)
    sameNum  = 0
    for i in dir['list']:
        if tc.compare(i,tagStr):
            sameNum +=1
    if sameNum > config.conf['SelectNodeNum']/2:
        dir['full'] =True
        return False
    else:
        dir['list'].append(tagStr)
        return True

def treeFilter(url,html,tree):
    """
    1. non-leaf-node
    2. leaf-node
    """
    treePath = gen_tree_path(url)
    tagStr = tc.genTagStr(html)
    if tree.has_key(treePath):
        if tree[treePath]['full'] == True:
            return False

        if len(tree[treePath]['list']) > int(config.conf['MaxNode']):
            return checkSimi(tagStr,tree[treePath])
        else:
            tree[treePath]['list'].append(tagStr) 
            return True
    else:
        tree[treePath] = {'full':False,'list':[tagStr]}
        return True


'''
def crawl(req,tree):
    # begin crawler
    req._timeout = config.conf['connTimeout'] 
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
        pass
        #print '[Spider Error]: ',err,' Url: ',req._url

    #cha chong
    if tf.treeFilter(req._url,html,tree)==False:
        return []


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
            
