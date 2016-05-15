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
        options = content.find_all(name='option')
        if len(options) != 0:
            try:
                self._value = options[0].attrs['value']
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
        soup = BeautifulSoup(content)
        #raw_input('')

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
            #raw_input('')
            try:
                if child.attrs['name'] == '':
                    continue
            except Exception as err:
                continue
            self._textareas.append(TextArea(child))

        # generate queries from input, textarea and select
        query = ''

        checkboxCount = False
        for child in self._inputs:
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
            query = query + child._name + '=' + child._value + '&'
        
        for child in self._selects:
            query = query + child._name + '=' + child._value + '&'

        if len(query) > 0 and query[len(query)-1] == '&':
            query = query[0:len(query)-1]
        
        queryDic = {}
        try:            
            for i in query.split('&'):
                k,v = i.split('=')
                queryDic[k] = v 
        except Exception as err:
            print err
        self._url = urlparse.urljoin(base,self._action)
        self._query = queryDic
                  
    def getUrl(self):
        return self._url
    def getReq(self):
        return request.Request(self._base,self._url,self._method,self._query,source='form')
    def getMethod(self):
        return self._method
    def getPayload(self):
        return self._query
