
1. Account 

```py
 accountSchema = {
            "profile_id":"P-001"
            "account_id" = "AC-001"
            "account_balance":float(0),
            "is_activate": True , # aa acount thi trad thava joyye ke ni te 
            "trad_indexs": [], # jenje  index aa account ma use karsu te index 
            "strategy":"", # kayi Strategy par aa account work karse te 
            "max_trad_per_day":10, # dayli avarage(Max) trad atli j levay 
            "todays_margin":float(10000), # ek day me ketla rupiya use thava joyye  a
            "todays_trad_margin":float(2000),# ek trad ma atla rupiya use thay 
            "account_min_profile":float(0), # One day ma minimum  Atlu profite thava j joye  jo ana thi vadhare thay ne to ana thi osu to ni j thava joyye 
            "account_max_loss":float(0), # One day ma max atlu j loss thava joyye 
            "base_stoploss": float(20),
            "base_target": float(30),
            "trailing_status":True , # trailing karvu ke ni te 
            "trailing_stoploss":float(10),
            "trailing_target":float(15),
            "payment_status":"Paper Trad" #Paper trad or Realmoney  for trading 
            "last_updated_datetime":"" # update thay day ma ek var te no datetime 
        }
        #  aa schema daily update thase accroding balanece ne situation pramane 
```


2. Order 

```py
order = {
    "order_id": "ORD123456",
    "profile_id": "PROF789",
    "account_id": "ACC987",
    "strategy": "Moving Average Crossover",
    "date": "2024-04-08",
    "trad_status": "Open",
    "trad_type": "Market",
    "trad_index": "S&P 500",
    "trad_side": "Buy",
    "trigger_index": "NASDAQ",
    "option_symbol": "AAPL",
    "qnty": 100,
    "buy_price": 150.25,
    "sell_price": None,
    "stoploss_price": 145.50,
    "target_price": 160.00,
    "buy_datetime": "2024-04-08 10:30:00",
    "sell_datetime": None,
    "pnl_status": "Open",
    "pnl": None
}


```


















