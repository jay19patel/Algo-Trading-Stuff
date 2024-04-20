from FilerDataSet import GetMainDataSet
from RowDataset import fyers_Dataset


def UpdatePipeline():
    fyers_Dataset( Symbol = "NSE:NIFTY50-INDEX",TimeFrame = "5",filename = "Private/Nifty50_5min.csv")
    fyers_Dataset( Symbol = "NSE:NIFTY50-INDEX",TimeFrame = "1D",filename = "Private/Nifty50_day.csv")
    GetMainDataSet()
    print("Update PIPELINE Sucessful")

UpdatePipeline()