from hashlib import md5
from time import time


def create_secret():
    return md5(str(time()).encode()).hexdigest()
