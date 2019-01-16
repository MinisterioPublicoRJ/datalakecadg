import json
from django.conf import settings
from hdfs import InsecureClient


hdfsclient = InsecureClient(settings.HDFS_URL, settings.HDFS_USER)
methodmap = json.load(open(settings.METHOD_MAP, 'r'))
