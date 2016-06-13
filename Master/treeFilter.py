# coding=utf-8
import sys
import re
import request
import urlparse
import chardet
import tagComp as tc
import formParse
import random
import config.config as config
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



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
    '''
    1. non-leaf-node
    2. leaf-node
    '''
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
            
