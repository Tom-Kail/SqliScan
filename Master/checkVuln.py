# coding=utf-8
import request
import result
import config.config as config
import scripts.sqli.bsqli_response_diff as bsqlitf
import scripts.sqli.bsqli_time_delay as bsqlitd
import scripts.sqli.sqli as sqli
from color_printer import colors
import time


# write log int log file 
def write_vuln_log(rst,fileName):
	# url, vulnName,payload, req, rsp
	f = open(fileName,'a')
	url = ''
	query = {}
	payload = ''
	advice = ''
	vulnName = ''
	method = ''
	if len(rst._req) != 0:
		req = rst._req[0]
		url = req._url
		method = req._method.upper()
		query = str(req._query)
		advice = rst._advice
		vulnName = rst._vulnName
		payload = '\n'.join(rst._payload)

	f.write('\n---')
	f.write('\nURL:%s (%s)'%(url,method))
	f.write('\nVulnName: %s'%vulnName)
	f.write('\nQuery: %s'%query)
	f.write('\nPayload: %s'%payload)
	f.write('\nAdvice: %s'%advice)
	f.write('\n---')
	f.close()

def check(req):
	try:
		if req._query == {}:
			return None

		rsp = sqli.start(req)
		if rsp != None:
		    return rsp

		rsp2 = bsqlitf.start(req)
		if rsp2 != None:
			return rsp2

		rsp3 = bsqlitd.start(req)
		if rsp3 != None:
			return rsp3
            
 	except Exception as err:
		print '[Check Vuln Error]: ',err
		return None

def start(req,fileName):
	rsp = check(req)

	if rsp != None:
		colors.red("Find Vuln")
		write_vuln_log(rsp,fileName)
	else:
		colors.green('rsp is None')