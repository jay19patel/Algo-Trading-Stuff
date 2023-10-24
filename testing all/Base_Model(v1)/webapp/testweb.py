import streamlit as st
import pandas as pd
import numpy as np
import datetime

# Generate fake data for the dashboard (replace this with real data)
fake_data = {
    "Nifty50_list": {
        "row_data": {
            "metadata": {
                "last": 15000.0,
                "change": 50.0,
                "percChange": 0.33,
                "open": 14980.0,
                "previousClose": 14950.0,
                "high": 15050.0,
                "low": 14970.0,
            }
        }
    },
    "pcr": 0.78,
    "Nifty50_chain": {
        "pe_suport": [(14800.0, 25000), (14750.0, 28000), (14700.0, 32000)],
        "ce_resistance": [(15100.0, 21000), (15150.0, 18000), (15200.0, 15000)],
    },
    "Nifty50_companies": {
        "downfall_no": 10,
        "upfall_no": 10,
        "max_chnage_com_down": [
            {"com_name": "Company1", "com_today_change": -2.5},
            {"com_name": "Company2", "com_today_change": -1.8},
            # Add more data here
        ],
        "max_chnage_com_up": [
            {"com_name": "Company3", "com_today_change": 3.2},
            {"com_name": "Company4", "com_today_change": 2.7},
            # Add more data here
        ],
    },
    "last_update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}


def sidebar1(mydata):
    optiondata = mydata["Nifty50_list"]["row_data"]["metadata"]["last"]
    vix = 11.48
    max_strike = round((optiondata + ((float(vix) / 19.10) * 100)), 2)
    min_strike = round((optiondata - ((float(vix) / 19.10) * 100)), 2)
    st.sidebar.code(f"India VIX : {vix}")
    st.sidebar.code(f"Today's Max Price : {max_strike}")
    st.sidebar.code(f"Today's Min Price : {min_strike}")

    pcr = mydata["pcr"]
    st.sidebar.code(f"Put Call Ratio : {pcr}")


def nifty50index(mydata):
    nifty_data = mydata["Nifty50_list"]["row_data"]["metadata"]
    st.divider()
    st.code(
        f"NIFTY 50 VALUE: {nifty_data['last']}   NIFTY 50 CHANGE: {round(nifty_data['change'], 2)}   NIFTY 50 CHANGE(%): {nifty_data['percChange']}"
    )
    st.code(
        f"OPEN: {nifty_data['open']}      CLOSE: {nifty_data['previousClose']}      HIGH: {nifty_data['high']}      LOW: {nifty_data['low']}"
    )
    st.divider()


def nifty_future(mydata):
    st.selectbox("Select Future Option", options=[1, 2, 3])
    st.subheader(f"Nifty 50 Future :blue[{19800}]")
    st.code(f"OI : {205593}                 CHANGE OI : {117373}              IV : {11.96}")
    st.code(f"LAST PRICE : {110}            PRICE CHANGE : {-112}             VOLUME : {3966600}")
    st.code(f"TOTAL BUY QNT : {902450}      TOTAL SELL QNT : {1309250}        BUY/SELL : {0.68}")


def support_resistance_index(mydata):
    support_index = mydata["Nifty50_chain"]["pe_suport"]
    resistance_index = mydata["Nifty50_chain"]["ce_resistance"]
    st.subheader(f":green[Support] And :red[Resistance] :blue[Nifty 50 Index]")
    s_list1 = [item[0] for item in support_index]
    s_list2 = [item[1] for item in support_index]
    r_list1 = [item[0] for item in resistance_index]
    r_list2 = [item[1] for item in resistance_index]
    data = {
        "Support": s_list1,
        "Support OI": s_list2,
        "Resistance": r_list1,
        "Resistance OI ": r_list2,
    }
    index = range(1, len(data["Support"]) + 1)
    dataframe = pd.DataFrame(data, index=index)
    st.table(dataframe)


def nifty_company(com_data):
    st.code(
        f"Down Fall Companies : {com_data['Nifty50_companies']['downfall_no']}                        Up Fall Companies : {com_data['Nifty50_companies']['upfall_no']}"
    )
    data = {
        "DownFall Company": [item["com_name"] for item in com_data["Nifty50_companies"]["max_chnage_com_down"]],
        "DF Change": [item["com_today_change"] for item in com_data["Nifty50_companies"]["max_chnage_com_down"]],
        "UpFall Company": [item["com_name"] for item in com_data["Nifty50_companies"]["max_chnage_com_up"]],
        "UF Change": [item["com_today_change"] for item in com_data["Nifty50_companies"]["max_chnage_com_up"]],
    }
    dataframe = pd.DataFrame(data)
    st.dataframe(dataframe)


# Side Bar
st.text(f"Last Update Time: {fake_data['last_update_time']}")
chain = st.sidebar.selectbox(label="Select Chain", options=["Home", "Nifty 50", "Nifty Company"], key="mark12")
if chain == "Home":
    st.title(f' :blue[{chain}] :sunglasses:')
    st.text("This is a simple Dashboard for Analyzing Some Data for Stock Option Chain :>")
    market_state = "Closed"
    if market_state == "Closed":
        st.warning("Market is Closed")
    nifty50index(fake_data)

elif chain == "Nifty 50":
    st.title(f' Stock Market :blue[{chain}] :sunglasses:')
    nifty50index(fake_data)
    support_resistance_index(fake_data)
    nifty_future(fake_data)

elif chain == "Nifty Company":
    st.title(f' Analysis :blue[{chain}] :sunglasses:')
    nifty_company(fake_data)
