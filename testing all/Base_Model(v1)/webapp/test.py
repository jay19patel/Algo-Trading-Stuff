

def test(mydata):
    if mydata['status'] == "Open":
        print("test",mydata)
    elif mydata['status'] == "Close":
        print("Market is Closed !!")
    else:
        print("Somthing Wrong !! :< ")
    
