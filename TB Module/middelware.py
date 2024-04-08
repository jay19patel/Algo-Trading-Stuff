def check_authentication(func):
    def wrapper(self, *args, **kwargs):
        if not self.isAuthenticated:
            print("Authentication required.")
        else:
            return func(self, *args, **kwargs)
    return wrapper


import datetime 
import random
def create_uuid(name):
    randint = random.randint(111, 999)
    mytimestampstr = str(datetime.datetime.now().timestamp()).replace(".", "")
    myuuid = f"{name}-{mytimestampstr}{randint}"
    print(myuuid)
    
    
def tbCurrentTimestamp():
    return datetime.datetime.now()

