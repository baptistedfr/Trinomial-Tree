import streamlit as st
from main import generate_and_price
from PythonFiles.market import Market
from PythonFiles.options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption, DigitalCallOption, DigitalPutOption
from datetime import datetime
import pandas as pd

st.title("Trinomial Tree Pricer")
st.header("Price your option :")

st.subheader("Market parameters :")
col1, col2 = st.columns(2)
with col1:
    spot = st.number_input("Spot", value=100)
    rate = st.number_input("Risk free rate", value=0.05)
with col2:
    vol = st.number_input("Volatility", value=0.20)
    div_date = st.date_input("Dividend date")

st.subheader("Option parameters :")
col1, col2 = st.columns(2)
with col1:
    strike = st.number_input("Strike", value=100)
    div = st.number_input("Dividend", value=0)
with col2:
    maturity = st.number_input("Maturity (in Years)", value=1)
    start_date = st.date_input("Start date of the contract")

st.subheader("Model parameters :")
col1, col2 = st.columns(2)
with col1:
    nb_steps = st.number_input("Number of steps", value=1000)
    is_greeks = st.checkbox("Calculate Greeks ?", value=False)
with col2:
    prunning_value = st.number_input("Prunning treshold (number of decimals)", value=8)
    prunning_value = 10 ** (-prunning_value)
    is_visu = st.checkbox("Visualise ?", value=False)

price_button = st.button("Compute option price")
if price_button:
    with st.spinner("In progress..."):
        market = Market(spot=spot, rate=rate, volatility=vol,div_date=div_date, dividende=div)
        option = EuropeanCallOption(time_to_maturity=maturity, strike=strike, start_date=start_date)
        info_dict, greeks_dict, fig = generate_and_price(market=market, option=option, nb_steps=nb_steps, prunning=prunning_value, visualise=is_visu, greeks=is_greeks)
        st.write("---")
        st.header("Results")
        st.subheader("Pricing :")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Option price : {info_dict["Price"]}")
        with col2:
            st.write(f" VS Close formula price : {info_dict["Benchmark Price"]}")
        
        st.subheader("Performance")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Tree generated in : {info_dict["Time Generate"]} sec")
        with col2:
            st.write(f"Option priced in : {info_dict["Time Price"]} sec")
        
        if greeks_dict is not None :
            st.subheader("Option greeks :")
            df = pd.DataFrame(list(greeks_dict.items()), columns=["Option Greeks", "Value"])
            df.style.hide(axis='index')
            st.table(df)

        if nb_steps >= 25:
            st.warning("Cannot visualize more than 25 steps")
        else :
            if fig is not None :
                st.pyplot(fig)