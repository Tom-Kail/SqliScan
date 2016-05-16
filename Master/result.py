# encoding=utf-8
import request
import requests
class Result(object):
	def __init__(self,req,rsp,payload,advice = '',vulnName = '',db='unknown'):
		self._req = req
		self._advice = advice
		self._vulnName = vulnName
		self._db = db
		self._rsp = rsp
		self._payload = payload