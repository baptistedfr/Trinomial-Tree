from PythonFiles.options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption
from PythonFiles.visualisation import visualize_tree
from datetime import datetime
from PythonFiles.market import Market
from PythonFiles.tree import Tree
import time
import numpy as np
from tqdm import tqdm

# option = AmericanPutOption(market=market, time_to_maturity=1, strike=105, start_date=datetime(2024,1,1), div_date=datetime(2024,2,1), dividende=0)
# option = BermudeanPutOption(market=market, time_to_maturity=1, strike=105, start_date=datetime(2024,1,1), div_date=datetime(2024,2,1), dividende=0, exercise_dates=[datetime(2024,4,1), datetime(2024,8,1)])


def generate_and_price(visualise : bool = False):
    nb_steps = 10000
    market = Market(spot=100, rate=0.05, volatility=0.2,div_date=datetime(2024,2,1), dividende=0)
    option = EuropeanPutOption(time_to_maturity=1, strike=95, start_date=datetime(2024,1,1))
    tree = Tree(market=market, option=option, nb_steps=nb_steps)
    print(f"Number of steps : {nb_steps}")

    start=time.time()
    tree.generate_tree()
    print(f"Tree generated in : {round(time.time()-start,5)} sec")

    start=time.time()
    tree.price()
    print(f"Option priced in : {round(time.time()-start,5)} sec")

    print(f"Option price with tree : {tree.root_node.payoff}")
    print(f"Option price with B&S (or MC): {option.compute_price(market)}")
    
    if visualise:
        visualize_tree(tree)

# generate_and_price(False)
# print("End")

# Ecart * Nb Step

market = Market(spot=100, rate=0.05, volatility=0.2,div_date=datetime(2024,2,1), dividende=0)
option = EuropeanCallOption(time_to_maturity=1, strike=100, start_date=datetime(2024,1,1))
def analyse(nb_steps, market, option):
    tree = Tree(market = market, option=option, nb_steps=nb_steps)
    start=time.time()
    tree.generate_tree()
    start=time.time()
    tree.price()
    temps_exec = round(time.time()-start,5)
    return [tree.root_node.payoff, temps_exec]

prices = []
execution_times = []
steps = np.arange(start = 1, stop = 1000, step=1)


for step in tqdm(range(len(steps)), total=len(steps), desc="Calculting Prices for steps", leave=False):
    result = analyse(steps[step], market, option)
    prices.append(result[0])          # Ajoute le prix au vecteur
    execution_times.append(result[1])  # Ajoute le temps d'exécution au vecteur

# Convertir les listes en tableaux NumPy si nécessaire
prices_array = np.array(prices)
execution_times_array = np.array(execution_times)


