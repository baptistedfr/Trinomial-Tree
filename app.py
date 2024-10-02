import streamlit as st
from main import generate_and_price
from PythonFiles.market import Market
from PythonFiles.options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption, DigitalCallOption, DigitalPutOption
from datetime import datetime

st.title("Trinomial Tree Pricer")

st.header("Price your option :")

nb_steps = st.number_input("Number of steps")
prunning_value = 1e-10

spot = st.number_input("Spot")
strike = st.number_input("Strike")
vol = st.number_input("Volatility")
rate = st.number_input("Risk free rate")
maturity = st.number_input("Maturity (in Years)")

start_date = st.date_input("Start date of the contract")
div_date = st.date_input("Dividend date")
div = st.number_input("Dividend")

is_greeks = st.checkbox("Calculate Greeks ?")
is_visu = st.checkbox("Visualise ?")

if st.button("Compute option price"):
    market = Market(spot=spot, rate=rate, volatility=vol,div_date=div_date, dividende=div)
    option = EuropeanCallOption(time_to_maturity=maturity, strike=strike, start_date=start_date)

    price = generate_and_price(market=market, option=option, prunning=prunning_value, visualise=is_visu, greeks=is_greeks)
    st.text(f"Option Price : {price}")