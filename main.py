from PythonFiles.options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption, DigitalCallOption, DigitalPutOption
from PythonFiles.greeks import compute_greeks
from PythonFiles.visualisation import visualize_tree
from datetime import datetime
from PythonFiles.market import Market
from PythonFiles.tree import Tree
import time
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

def generate_and_price(market, option, nb_steps : int, prunning : float, visualise : bool = False, greeks : bool = False):

    tree = Tree(market=market, option=option, nb_steps=nb_steps, prunning_value=prunning)
    print("\n-----------------------------------------------")
    print(f"Number of steps : {nb_steps}")

    print("\nPerformance :")
    start=time.time()
    tree.generate_tree()
    timer_generate = round(time.time()-start,5)
    print(f"Tree generated in : {timer_generate} sec")

    start=time.time()
    tree.price()
    timer_price = round(time.time()-start,5)
    print(f"Option priced in : {timer_price} sec")

    print("\nPricing :")
    price = tree.root_node.payoff
    close_formula_price = option.compute_price(market)
    print(f"Option price with tree : {price}")
    print(f"Close formula price : {close_formula_price}")
    
    fig, greeks_dict = None, None
    if visualise and nb_steps < 25:
        fig = visualize_tree(tree)
    if greeks:
        greeks_dict = compute_greeks(tree, market, option, nb_steps, prunning)
    print("-----------------------------------------------")

    info_dict = {"Price" : price, "Benchmark Price" : close_formula_price, "Time Generate" : timer_generate, "Time Price" : timer_price}
    return info_dict, greeks_dict, fig

def analyse(nb_steps, market, option):
    tree = Tree(market = market, option=option, nb_steps=nb_steps, prunning_value=1e-10)
    start=time.time()
    tree.generate_tree()
    tree.price()
    temps_exec = round(time.time()-start,5)
    return [tree.root_node.payoff, temps_exec]

def generate_graphs():
    market = Market(spot=100, rate=0.05, volatility=0.2,div_date=datetime(2024,2,1), dividende=0)
    option = EuropeanCallOption(time_to_maturity=1, strike=100, start_date=datetime(2024,1,1))
    prices = []
    execution_times = []
    steps = [1] + [x for x in range (5,50,5)] + [x for x in range (50,500,25)] + [x for x in range (500,1000,50)] + [x for x in range (1000,2500,100)]


    for step in tqdm(range(len(steps)), total=len(steps), desc="Calculting Prices for steps", leave=False):
        result = analyse(steps[step], market, option)
        prices.append(result[0])          # Ajoute le prix au vecteur
        execution_times.append(result[1])  # Ajoute le temps d'exécution au vecteur

    # Convertir les listes en tableaux NumPy si nécessaire
    prices_array = np.array(prices)
    execution_times_array = np.array(execution_times)
    bs_price = option.compute_price(market)
    gap = bs_price - prices_array
    gap_step = gap * steps
    # --------- 1er Graphique: Price vs Steps -----------
    plt.figure(figsize=(12, 5))

    # Création du premier sous-graphique
    plt.plot(steps, prices_array, label='Computed Prices')
    plt.axhline(y=bs_price, color='r', linestyle='--', label=f'BS Price: {round(bs_price,2)}')
    plt.title('Price vs Steps')
    plt.xlabel('Steps')
    plt.ylabel('Price')
    plt.legend()
    plt.tight_layout()
    plt.show()
    # --------- 2ème Graphique: Execution Time vs Steps -----------
    plt.figure(figsize=(12, 5))
    plt.plot(steps, execution_times_array, color='green', label='Execution Time')
    plt.title('Execution Time vs Steps')
    plt.xlabel('Steps')
    plt.ylabel('Execution Time (seconds)')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # --------- 3ème Graphique: Gap (BS Price - Computed Prices) -----------
    plt.figure(figsize=(12, 5))
    plt.plot(steps, gap, color='purple', label='Difference')
    plt.title('Difference (BS Price - Computed Prices) vs Steps')
    plt.xlabel('Steps')
    plt.ylabel('Difference')
    plt.axhline(y=0, color='black', linestyle='--')  # Ligne pour montrer la différence nulle
    plt.legend()
    plt.tight_layout()
    plt.show()

    # --------- 4ème Graphique: Gap*Step (BS Price - Computed Prices) -----------
    plt.figure(figsize=(12, 5))
    plt.plot(steps, gap_step, color='orange', label='Difference*Pas')
    plt.title('Difference (BS Price - Computed Prices) vs Steps')
    plt.xlabel('Steps')
    plt.ylabel('Difference')
    plt.axhline(y=0, color='black', linestyle='--')  # Ligne pour montrer la différence nulle
    plt.legend()
    plt.tight_layout()
    plt.show()

nb_steps = 1000
prunning = 1e-10

market = Market(spot=100, rate=0.05, volatility=0.2,div_date=datetime(2024,1,5), dividende=3)
option = EuropeanPutOption(time_to_maturity=1, strike=100, start_date=datetime(2024,1,1))

generate_and_price(market=market, option=option, nb_steps=nb_steps, prunning=prunning, visualise=False, greeks=False)