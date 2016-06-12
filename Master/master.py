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
import threading
import checkVuln
import tagComp as tc
import config.config as config
from threadpool import ThreadPool
from color_printer import colors
from bs4 import BeautifulSoup
from posixpath import normpath
import getopt
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
tree = {}


def startCheck(*args, **kwds):
    checkVuln.start(args[0],args[1])

def create_logfile(seedUrl):
    tup = urlparse.urlparse(seedUrl)
    host = tup.netloc
    now = time.localtime()
    dirName = 'log/'
    logName =dirName + host + '_'+ time.strftime('%Y%m%d%H%M%S',now)
    logfile = open(logName,'w')
    logfile .write('目标：'+ seedUrl + ' (GET)\n')
    logfile.close()
    return logName

def start_proxy():
    os.system('ps -ef | grep -v grep | grep proxy.py | awk \'{print $2}\'|xargs kill -9')
    os.system('python proxy.py --hostname 127.0.0.1 --port 8899 --log-level ERROR')

def getCookie(loginUrl):
    colors.green('您想要进行cookie录制吗(y/N)')


    while True: 
        finish = raw_input('')
        i = finish.lower().lower() 
        if i == 'n' or i == '\n' or i == '\r' or i=='':
            return  {}
        else:
            break
    th = threading.Thread(target=start_proxy)
    th.start()
    if loginUrl == '':
        return ''
    # recording cookie
    try:
        webbrowser.open_new(loginUrl)
    except Exception as err:
        print ''

    colors.yellow( '如果您已经完成了cookie录制，请在控制台中输入 Y')
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
    print  "cookie:"
    print cookie
    return cookie

def advice():
    ad = """
    防御SQL注入漏洞的建议：

    [1] 库或框架

        使用能够防御SQL注入漏洞的库或框架。

    [2] 参数化

        尽量使用自动实施数据和代码之间的分离的结构化机制。
        这些机制也能够自动提供相关引用、编码和验证，而不是依赖于开发者在生成输出的每一处提供此能力。

    [3] 环境固化

        使用完成必要任务所需的最低特权来运行代码。

    [4] 输出编码

        如果在有风险的情况下仍需要使用动态生成的查询字符串或命令，请对参数正确地加引号并将这些参数中的任何特殊字符转义。

    [5] 输入验证

        假定所有输入都是恶意的。
        使用“接受已知善意”输入验证策略：严格遵守规范的可接受输入的白名单。
        拒绝任何没有严格遵守规范的输入，或者将其转换为遵守规范的内容。
        不要完全依赖于通过黑名单检测恶意或格式错误的输入。但是，黑名单可帮助检测潜在攻击，或者确定哪些输入格式不正确，以致应当将其彻底拒绝。

    """
    return ad
def readReffer():
    f = open("reffer.txt","r")
    content  = f.read()
    f.close()
    urls = content.split(' ')
    reqs = []
    # may have some post request in urls, 
    for x in urls:
        req = request.Request(base="",url=x,timeout=config.conf['connTimeout'],query={},method='get')
        reqs.append(req)
        print x._url
    return reqs
    
def start(baseUrl,seedUrl):
    # clean reffer in reffer.txt
    f = open("reffer.txt","w")
    f.close()

    #seed = Request(base='http://192.168.42.131/dvwa/index.php',url='http://192.168.42.131/dvwa/index.php',method='get')
    seed = request.Request(base=baseUrl,url=seedUrl,timeout=config.conf['connTimeout'],query={},method='get')
    #seed = request.Request(base='http://192.168.42.132/dvwa/',url='http://192.168.42.132/dvwa/',query={},method='get')
    colors.blue( '种子URL： %s\n'%seed._url)
    logfileName = create_logfile(seed._url)
    cookie = getCookie(seed._url)
    
    # begin crawler
    tup = urlparse.urlparse(seed._url)
    netloc = tup.netloc # seed url 
    count = 1
    q = Queue.Queue()
    bf = bloomFilter.BloomFilter(0.001,100000)
    # readreffer from reffer.txt
    '''
    reffer = readReffer()
    reqSet = []
    reqSet.append(seed)
    reqSet.extend(reffer)
    for i in reqSet:
        q.put(i)
        bf.insert(i._url)
    '''
    q.put(seed)
    bf.insert(seed._url)

    nums = config.conf['MaxThread']
    pool = ThreadPool(nums)
    begin = time.time()
    while(not q.empty()):
        
        req = q.get()
        print 'URL: ',req._BFUrl,'  ', req._source
        req._cookies = cookie

        
        if req._query != {} :
            count += 1 
            pool.add_task(startCheck,req,logfileName)
        reqs = crawler.crawl(req,tree)
        # prase url by bloomFilter and treeFilter ?
        for x in reqs:
            if not bf.exist(x._BFUrl):
                bf.insert(x._BFUrl)
                q.put(x)


    pool.destroy()
    end = time.time()
    
    f = open(logfileName,'r')
    colors.blue('\n扫描结果：\n\n')
    x  = f.read()
    colors.green(x)
    colors.blue('\n扫描结果已保存在 "%s"\n\n'%(os.getcwd()+'/'+logfileName)+' 中')
    cost = end - begin 
    print "耗时：%f秒"%cost
    print "进行测试的URL数量：",count
    f.close()
    f = open(logfileName,'a')
    f.write(advice())
    f.close()
    os.system('ps -ef | grep -v grep | grep proxy.py | awk \'{print $2}\'|xargs kill -9')


def Usage():
    print 'SQLIScan 使用方法:\n'
    print '\t-h,--help:\t帮助信息\n'
    print '\t-u,--url:\t种子URL\n'
    print '\t--thread:\t最大线程数 \n'
    print '\t--version:\t打印版本信息 \n'
def Version():
    print 'SQLIScan 1.0.0'

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'hvu:m:t:e:', ['help','thread=', 'version','url=','maxnode=','eqlimit','thread='])
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
            # 1. http://xxx
            # 1. http://xxx
            if len(v) < 4:
                config.conf['url'] = 'http://'+v
            elif len(v)>4 and v[0:4].lower()!='http':
                config.conf['url'] = 'http://'+v
            elif len(v)>4 and v[0:4].lower()=='http':
                config.conf['url'] = v

        elif k in ('--thread',):
            config.conf['MaxThread'] = int(v)
        elif k in ('-e','--eqlimit'):
            config.conf['EqLimit'] = float(v)
        elif k in ('-t','--timeout'):
            config.conf['connTimeout'] = float(v)
        elif k in ('-m','--maxnode'):
            #MaxNode = v
            config.conf['MaxNode'] = int(v)

        else:
            print '无效选项！'
            sys.exit(3)
    if config.conf['url'] =='':
        colors.red('请输入URL！')
        Usage()
        sys.exit()
    else:
        colors.blue('开始扫描\n')
        start(config.conf['url'],config.conf['url'])


if len(sys.argv) == 1:
    colors.red('请输入URL！')
    Usage()
    sys.exit()
else:
    main(sys.argv)