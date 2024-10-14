from datetime import datetime
import time
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from PythonFiles.options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption, DigitalCallOption, DigitalPutOption
from PythonFiles.greeks import compute_greeks
from PythonFiles.visualisation import visualize_tree, plot_price_convergence, plot_execution_time, plot_gap, plot_gap_step
from PythonFiles.utils import generate_graphs
from PythonFiles.market import Market
from PythonFiles.tree import Tree
from PythonFiles.treeMemoryAlloc import TreeMemoryAlloc
##### A ENLEVER
nb_steps = 10
prunning = 1e-8

# market = Market(spot=100, rate=0.03, volatility=0.21,div_date=datetime(2024,6,15), dividende=0)
# option = EuropeanCallOption(time_to_maturity=0.8219, strike=101, start_date=datetime(2024,3,1))
# generate_and_price(market=market, option=option, nb_steps=nb_steps, prunning=prunning, visualise=True, greeks=True) 

# tree = TreeMemoryAlloc(market=market, option=option, nb_steps=nb_steps, prunning_value=prunning)
# start=time.time() 
# print(tree.price_tree())
# timer_price = round(time.time()-start,5)
# print(f"Option priced in : {timer_price} sec")

generate_graphs()