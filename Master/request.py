
# encoding=utf-8
import requests
import urlparse
import config.config as config
import copy
import time
import random

class Request(object):
    def __init__(self,base,url,method='get',query={},cookie={},timeout=1,source='regex'):
        tmpUrl = my_join(base,url)
        self._url = my_join(base,url)
        self._method = method.lower()
        if query == {} and self._method == 'get':
            query = get_query_from_url(self._url)
            self._url = strip_query(self._url)

        self._query = query
        self._timeout = timeout
        self._cookies = cookie
        self._BFUrl = '' # like ID to identify unique request
        self._source = source
        tup = urlparse.urlparse(self._url)
        # self._url has two kind:
        # 1. *?*
        # 1. 
        # self._url + self._query + self._method
        self._BFUrl = self._url + "?"
        if tup.query != '':
            self._BFUrl += tup.query + "&"

        tmp = ""
        for i in self._query:
            tmp +=  i + '=' + self._query[i] + '&'
        if len(tmp) >0 and tmp[-1] == '&':
             tmp = tmp[:-1]
        self._BFUrl += tmp
        self._BFUrl += '\t'+self._method        
        '''
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
            self._BFUrl = self._BFUrl + self._url + '?'
            for k in query.keys():
                self._BFUrl = self._BFUrl + k + '&'
        '''
def get_query_from_url(url):
    if url == '':
        return {}
    queryStr = urlparse.urlparse(url).query
    if queryStr == '':
        return {}
    try:
        queryList = queryStr.split('&')
        queryDict = {}
        for i in queryList:
            k, v = i.split('=')
            queryDict[k] = v
        return queryDict
    except Exception as err:
        '''
        print '\n--------'
        print 'queryStr: ',queryStr
        print 'url: ',url
        print err
        print '-------\n'
        '''
        return {} 

def strip_query(url):
    scheme, host, path, query, fragment = urlparse.urlsplit(url)
    return urlparse.urlunsplit((scheme, host, path, '', fragment))




def my_join(base,url): 
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

def get_payload_query_list(query,payload):
	'''
	example:
			query = {'name'='lili','pwd'='password'}
			payload = "' and 0"

	result:
			payloadDict = [{"name"="lili' and 0","pwd"="password"},{"name"="lili","pwd"="password' and 0"}]
	'''
	queryList = []
	for i in query:
		tmpQuery = copy.deepcopy(query)
		tmpQuery[i] = query[i] + payload
		queryList.append(tmpQuery)

	return queryList



def sendPayload(req,payloadQuery):
    tmpReq = copy.deepcopy(req)
    tmpReq._query = payloadQuery
    return sendRequest(tmpReq)

def sendRequest(req,tried=0):
    if tried == config.conf['MaxRetryTimes']:
        raise(requests.exceptions.ConnectTimeout)
    try:
        method = req._method.lower()
        if method == 'get':
            r = requests.get(req._url,timeout=req._timeout,cookies=req._cookies,params=req._query)
            return r
        elif method == 'post':
            r = requests.post(req._url,timeout=req._timeout,cookies=req._cookies,data=req._query)
            return r
        else:
            print '[Info]: Method '+ method +' not support!'
            return None
    except Exception as err:
        if type(err) == requests.exceptions.ConnectTimeout:
            time.sleep(random.random()/2) 
            sendRequest(req,tried+1)
        else:
            raise(err)


