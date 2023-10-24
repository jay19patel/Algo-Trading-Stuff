import streamlit as st
import datetime
import pandas as pd

def sidebar1(mydata):
    optiondata = mydata["Nifty50_list"]['row_data']["metadata"]["last"]
    vix = 11.48
    max_strike = round((optiondata+((float(vix)/19.10)*100)), 2)
    min_strike = round((optiondata-((float(vix)/19.10)*100)), 2)
    st.sidebar.code(f"India VIX :{vix}")
    st.sidebar.code(f"Today's Max Price :{max_strike}")
    st.sidebar.code(f"Today's Min Price :{min_strike}")

    pcr = mydata['pcr']
    st.sidebar.code(f"Put Call Ratio :{pcr}")



def nifty50index(mydata):
        # Main Container 
    nity_data = mydata["Nifty50_list"]['row_data']["metadata"]
    st.divider()
    st.code(f"NITY 50 VALUE :{nity_data['last']}   NITY 50 CHNAGE:{round(nity_data['change'],2)}   NIFTY 50 CHNAGE(%) :{nity_data['percChange']}")
    st.code(f"OPEN : {nity_data['open']}      CLOSE : {nity_data['previousClose']}      HIGH : {nity_data['high']}      LOW : {nity_data['low']}")  
    st.divider()


def nifty_future(mydata):
    st.selectbox("Selecte Future Option",options=[1,2,3])
    st.subheader(f"Nifty 50 Future :blue[{19800}]")
    st.code(f"OI : {205593}                 CHNAGE OI : {117373}              IV : {11.96}")
    st.code(f"LAST PRICE : {110}            PRICE CHNAGE : {-112}             VOLUME : {3966600}")  
    st.code(f"TOTAL BUY QNT : {902450}      TOTAL SELL QNT : {1309250}        BUY/SELL : {0.68}")  
    st.divider()


def support_resistance_index(mydata):
    support_index = mydata['Nifty50_chain']['pe_suport']
    resistance_index= mydata['Nifty50_chain']['ce_resistance']
    st.subheader(f' :green[Support] And :red[Resistance] :blue[Nifty 50 Index]')
    s_list1 = [item[0] for item in support_index]
    s_list2 = [item[1] for item in support_index]
    r_list1 = [item[0] for item in resistance_index]
    r_list2 = [item[1] for item in resistance_index]
    data = {
        "Support":s_list1,
        "Support OI":s_list2,
        "Resistance":r_list1,
        "Resistance OI ":r_list2,
    }
    index = range(1, len(data['Support']) + 1)
    dataframe = pd.DataFrame(data,index=index)
    st.table(dataframe)


def nifty_compny(com_data):
    st.code(f"Down Fall Companies : {com_data['Nifty50_list']['downfall_no']}                        Up Fall Companies : {com_data['Nifty50_list']['upfall_no']}")
    data ={
        "DownFall Company":[item["com_name"] for item in com_data['Nifty50_list']['max_chnage_com_down']],
        "DF Change":[item["com_today_change"] for item in com_data['Nifty50_list']['max_chnage_com_down']],
        "UpFall Company":[item["com_name"] for item in com_data['Nifty50_list']['max_chnage_com_up']],
        "UF Change":[item["com_today_change"] for item in com_data['Nifty50_list']['max_chnage_com_up']],

    }
    dataframe = pd.DataFrame(data) 
    st.dataframe(dataframe)
   


def webmain(mydata):
    # print(mydata)


    #  Side Bar 
    
    st.text(f"Last Update Time :{mydata['last_update_time']}")
    chain= st.sidebar.selectbox(label="Selecet Chain ",options=["Home","Nifty 50","Nifty Compny"],key="mark12")
    if chain == "Home":
        st.title(f' :blue[{chain}] :sunglasses:')
        st.text("This is simple Dashbord for Analysis Some Data for Steding Option chain :>")
        market_states = "Close"
        if market_states =="Close":
            st.warning("Market is Close ")
        nifty50index(mydata)

    elif chain == "Nifty 50":
        st.title(f' Stock Market :blue[{chain}] :sunglasses:')
        nifty50index(mydata)
        support_resistance_index(mydata)
        nifty_future(mydata)

    elif chain == "Nifty Compny":
        st.title(f' Analysis :blue[{chain}] :sunglasses:')
        nifty_compny(mydata)

    
    sidebar1(mydata)
