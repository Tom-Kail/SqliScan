# encoding=utf-8
import request
import requests
class Result(object):
	def __init__(req,rsp,payload):
		self._req = req
		self._rsp = rsp
		self._payload = payload