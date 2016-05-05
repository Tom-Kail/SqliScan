#coding=utf-8
from bs4 import BeautifulSoup
import lxml
import urlparse
import request

class Input(object):
    def __init__(self,content):
        try:
            self._name = content.attrs['name']
        except Exception as err:
            self._name = ''

        try:
            self._type = content.attrs['type']
        except Exception as err:
            self._type = 'text'
        
        try:
            self._value = content.attrs['value']        
        except Exception as err:
            self._value = 'cntvalue' #'cnt' are first characters of my PinYin name, I use it as default value of input tag
        finally:
            if self._value == '':
                self._value = 'cntvalue'
        try:
            self._checked = content.attrs['checked']
        except Exception as err:
            self._checked = ''
class TextArea(object):
    def __init__(self,content):
        try:
            self._name = content.attrs['name']     
        except Exception as err:
            self._name = ''

        try:
            self._value = content.attrs['value']        
        except Exception as err:
            self._value = ''
class Select(object):
    def __init__(self,content):
        #if select contains several options, use first option value as select defalult value
        try:
            self._name = content.attrs['name']
        except Exception as err:
            self._name = ''
        if len(content.contents) != 0:
            try:
                self._value = content.contents[0].attrs['value']
            except Exception as err:
                self._value = 'cntvalue'
        else:
            self._value = 'cntvalue'
class Form(object):
    def __init__(self,base,content):
        '''
        example of 'content':
           ' <form>
                <input name="name">
            </form>'
        'scheme', 'netloc' and 'path' come form parent url
        '''
        # parse form content
        soup = BeautifulSoup(content,'lxml')
        try:
            self._method = soup.form.attrs['method'].lower()
        except Exception as err:
            self._method = 'get'

        try:
            self._action = soup.form.attrs['action']
        except Exception as err:
            self._action = ''
        self._base = base
        self._inputs = []
        self._selects = []
        self._textareas = []
        for child in soup.find_all(name='input'):
            try:
                if child.attrs['name'] == '':
                    continue
            except Exception as err:
                continue
            self._inputs.append(Input(child))
        for child in soup.find_all(name='select'):
            try:
                if child.attrs['name'] == '':
                    continue
            except Exception as err:
                continue
            self._selects.append(Select(child))

        for child in soup.find_all(name='textarea'):
            try:
                if child.attrs['name'] == '':
                    continue
            except Exception as err:
                continue
            self._textareas.append(TextArea(child))

        # generate queries from input, textarea and select
        query = ''
        payload = {}
        checkboxCount = False
        for child in self._inputs:
            payload[child._name] = child._value
            if child._type == 'radio' and child._checked == 'checked':    
                query =query + child._name + '=' + child._value + '&'
            elif child._type == 'checkbox' and checkboxCount == False:
                query = query + child._name + '=' + child._value + '&'
                checkboxCount = True
            elif child._type == '' or child._type == 'text' or child._type == 'password':
                query = query + child._name + '=' + child._value + '&'
            else:
                query = query + child._name + '=' + child._value + '&'
       
        for child in self._textareas:
            payload[child._name] = child._value
            query = query + child._name + '=' + child._value + '&'
        
        for child in self._selects:
            payload[child._name] = child._value
            query = query + child._name + '=' + child._value + '&'
        # add query in action
        actionTup = urlparse.urlparse(self._action)
        query = query + actionTup.query
        if len(query) > 0 and query[len(query)-1] == '&':
            query = query[0:len(query)-1]
        
        for line in actionTup.query.strip().split('&'):
            if line == '':
                break
            name,value = line.strip().split('=',1)
            payload[name] = value 
        # use action and query to generate tmpUrl
        if self._method == 'get':
            tmpUrl = actionTup.path + '?' + query
            self._url = urlparse.urljoin(base,tmpUrl)
            self._query = {} 
        elif self._method == 'post':
            tmpUrl = actionTup.path
            self._url = urlparse.urljoin(base,tmpUrl)
            self._query = payload
        '''    
        # dirPath of parent url
        pos = path.rfind('/')
        dirPath = ''
        if pos != -1:
            dirPath = path[0:pos+1]
        else:
            dirPath = '/'
        tup = urlparse.urlparse(self._action)
        tmpUrl = ''
        # generate tmpUrl
        if tup.path == '':
            # current webpage
            tmpUrl = scheme + '://' + netloc + path + '?'
        elif tup.path.find('/') == -1:
            # like 'file2.php?a=one'
            tmpUrl = scheme + '://' + netloc + dirPath + tup.path + '?'
        elif tup.path[0] == '/':
            # like '/' or '/file.php?a=b'
            tmpUrl = scheme + '://' + netloc +tup.path + '?'
        else:
            pass
        # add query to tmpUrl
        if tup.query != '':
            tmpUrl = tmpUrl + tup.query + '&' + query
        else:
            tmpUrl = tmpUrl + query
        '''           
    def getUrl(self):
        return self._url
    def getReq(self):
        return request.Request(self._base,self._url,self._method,self._query,source='form')
    def getMethod(self):
        return self._method
    def getPayload(self):
        return self._query
