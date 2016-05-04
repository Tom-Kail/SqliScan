# encoding=utf-8
import requests
import copy

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

def getPayloadQueryList(query,payload):
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


def sendRequest(req):
    try:
        method = req._method.lower()
        if method == 'get':
            r = requests.get(req._url,timeout=1,cookies=req._cookies,params=req._query)
            return r
        elif method == 'post':
            r = requests.post(req._url,timeout=1,cookies=req._cookies,data=req._query)
            return r
        else:
            print '[Info]: Method '+ method +' not support!'

    except Exception as err:
        print '[Error]: ',err
    return None

