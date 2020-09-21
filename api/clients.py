from django.conf import settings
from hdfs.ext.kerberos import KerberosClient

hdfsclient = KerberosClient(settings.HDFS_URL)
