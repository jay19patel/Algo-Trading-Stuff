

import datetime 
import random

def create_uuid(name):
    randint = random.randint(111, 999)
    mytimestampstr = str(datetime.datetime.now().timestamp()).replace(".", "")
    myuuid = f"{name}-{mytimestampstr}{randint}"
    return myuuid

def tbCurrentTimestamp():
    return datetime.datetime.now()
