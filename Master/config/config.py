# coding=utf-8
import json
import os
conf = {}
def init():
    path = os.path.join(os.path.abspath('.'),"conf")
    f = open(path)
    conf = json.load(f)

init()
#if not "/root/WorkSpace/SqliScan/Master/config/" in sys.path:
#   sys.path.append("/root/WorkSpace/SqliScan/Master/config/")
