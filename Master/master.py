# coding=utf-8
#!/usr/bin/python
import Queue
import sys
import webbrowser
import re
import os
import request
import time
import bloomFilter
import urlparse
import formParse
import crawler
import checkVuln
import config.config as config
from threadpool import ThreadPool
from color_printer import colors
from bs4 import BeautifulSoup
from posixpath import normpath
import getopt

def startCheck(*args, **kwds):
    checkVuln.start(args[0],args[1])

def create_logfile(seedUrl):
    tup = urlparse.urlparse(seedUrl)
    host = tup.netloc
    now = time.localtime()
    dirName = 'log/'
    logName =dirName + host + '_'+ time.strftime('%Y%m%d%H%M%S',now)
    logfile = open(logName,'w')
    logfile .write('Target: '+ seedUrl + ' (GET)\n')
    logfile.close()
    return logName

def getCookie(loginUrl):
    colors.green('Do you want recording cookie?(y/N)')
    while True: 
        finish = raw_input('')
        i = finish.lower().lower() 
        if i == 'n' or i == '\n' or i == '\r' or i=='':
            return  {}
        else:
            break

    if loginUrl == '':
        return ''
    # recording cookie
    try:
        webbrowser.open_new(loginUrl)
    except Exception as err:
        pass
    colors.yellow( 'Please enter "Y" if you finishing recording cookie.')
    while True: 
        finish = raw_input('')
        if finish.lower() == 'y':
            break
        else:
            finish = ''
    # read cookie from cookieFile
    #print config.conf
    #cookieFileName = config.config.conf['CookieFileName']
    # cookieFileName = '/root/cntzapfile.txt'
    #print 'Read cookie from file: ',cookieFileName
    cookieFileName  =config.conf['CookieFileName']
    cookieTmp = open(cookieFileName,'r').read()
    cookie = {}
    try:
        if len(cookieTmp.strip()) != 0:
            for line in cookieTmp.split(';'):
                name,value = line.strip().split('=',1)
                cookie[name] = value
        print 'cookie is:',cookie
    except Exception as err:
        pass
    return cookie

tree = {}
def gen_tree_path(url):
    scheme, host, path, query, fragment = urlparse.urlsplit(url)
    path = '/' if path=='' else path[:path.rfind('/')+1]
    treePath = urlparse.urlunsplit((scheme,host,path,'',''))
    return treePath
def treeFilter(url):
    '''
    1. non-leaf-node
    2. leaf-node
    '''
    treePath = gen_tree_path(url)
    if tree.has_key(treePath):
        #if tree[treePath] > config.conf['MaxNode']:
        if int(tree[treePath]) > int(config.conf['MaxNode']):
            #print 'treePath:',tree[treePath],'\tmaxnode:',maxnode,'\tRst:','False'
            return False
        else:
            tree[treePath] +=1
            #colors.red( 'treePath:'+str(tree[treePath])+'\tmaxnode:'+str(maxnode)+'\tRst:'+'True')
            return True
    else:
        tree[treePath] = 1
        return True

def start(baseUrl,seedUrl):
    #seed = Request(base='http://192.168.42.131/dvwa/index.php',url='http://192.168.42.131/dvwa/index.php',method='get')

    seed = request.Request(base=baseUrl,url=seedUrl,timeout=config.conf['connTimeout'],query={},method='get')
    #seed = request.Request(base='http://192.168.42.132/dvwa/',url='http://192.168.42.132/dvwa/',query={},method='get')
    colors.green( 'seed url: %s'%seed._url)
    logfileName = create_logfile(seed._url)
    cookie = getCookie(seed._url)
    # begin crawler
    tup = urlparse.urlparse(seed._url)
    netloc = tup.netloc # seed url 
    count = 0
    q = Queue.Queue()
    q.put(seed)
    bf = bloomFilter.BloomFilter(0.001,100000)
    
    nums = config.conf['MaxThread']
    pool = ThreadPool(nums)
    
# Join and destroy all threads

    # !!! need deal with seed._url
    bf.insert(seed._url)
    while(not q.empty()):
        req = q.get()
        req._cookies = cookie

        count += 1 
        if req._query != {} :
            pool.add_task(startCheck,req,logfileName)
            #startCheck(req,logfileName)
        reqs = crawler.crawl(req)
        # test sqli vuln
        # prase url by bloomFilter and treeFilter ?
        for x in reqs:
            if not bf.exist(x._BFUrl) and treeFilter(x._url):
                #if not bf.exist(x._BFUrl) :
                bf.insert(x._BFUrl)
                q.put(x)


    pool.destroy()
    print "Number of url:",count
    f = open(logfileName,'r')
    colors.blue('\nScan result:\n\n')
    x  = f.read()
    colors.green(x)
    colors.blue('\nAbove is the result of scan, and the result is stored in file "%s"\n\n'%(os.getcwd()+'/'+logfileName))
    

def Usage():
    print 'SqliScan Usage:\n'
    print '\t-h,--help:\tprint help message.\n'
    print '\t-u,--url:\tseed url\n'
    print '\t-m,--maxnode:\tmax url num in one dir\n'
    print '\t-t,--timeout:\thttp request timeout\n'
    print '\t--thread:\tmax thread num \n'
    print '\t--version:\tprint version \n'
def Version():
    print 'SqliScan 1.0.0'

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'hu:m:t:', ['help','thread=', 'version','url=','maxnode=','thread='])
    except getopt.GetoptError, err:
        print str(err)
        Usage()
        sys.exit(2)
    config.conf['url'] = ''
    for k, v in opts:
        if k in ('-h', '--help'):
            Usage()
            sys.exit(1)
        elif k in ('-v', '--version'):
            Version()
            sys.exit(0)
        elif k in ('-u', '--url'):
            config.conf['url'] = v
        elif k in ('--thread',):
            config.conf['MaxThread'] = int(v)
        elif k in ('-t','--timeout'):
            config.conf['connTimeout'] = float(v)
        elif k in ('-m','--maxnode'):
            #MaxNode = v
            config.conf['MaxNode'] = int(v)

        else:
            print 'unhandled option'
            sys.exit(3)
    if config.conf['url'] =='':
        colors.red('please input url!')
        sys.exit()
    else:
        colors.blue('Start scanning')
        start(config.conf['url'],config.conf['url'])


if len(sys.argv) == 1:
    colors.red('please input url!')
    sys.exit()
else:
    main(sys.argv)