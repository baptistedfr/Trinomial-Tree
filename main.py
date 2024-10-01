from PythonFiles.options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption
from PythonFiles.visualisation import visualize_tree
from datetime import datetime
from PythonFiles.market import Market
from PythonFiles.tree import Tree
import time
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt


def generate_and_price(prunning, visualise : bool = False):
    nb_steps = 1000
    market = Market(spot=100, rate=0.05, volatility=0.2,div_date=datetime(2024,2,1), dividende=0)
    option = EuropeanCallOption(time_to_maturity=1, strike=100, start_date=datetime(2024,1,1))
    tree = Tree(market=market, option=option, nb_steps=nb_steps, prunning_value=prunning)
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

generate_and_price(1e-14, False)
print("End")

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


# prices = []
# execution_times = []
# steps = [1] + [x for x in range (5,50,5)] + [x for x in range (50,500,25)] + [x for x in range (500,1000,50)] + [x for x in range (1000,2500,100)]


# for step in tqdm(range(len(steps)), total=len(steps), desc="Calculting Prices for steps", leave=False):
#     result = analyse(steps[step], market, option)
#     prices.append(result[0])          # Ajoute le prix au vecteur
#     execution_times.append(result[1])  # Ajoute le temps d'exécution au vecteur

# Convertir les listes en tableaux NumPy si nécessaire
# prices_array = np.array(prices)
# execution_times_array = np.array(execution_times)
# bs_price = option.compute_price(market)
# gap = bs_price - prices_array
# gap_step = gap * steps
# # --------- 1er Graphique: Price vs Steps -----------
# plt.figure(figsize=(12, 5))

# # Création du premier sous-graphique
# plt.plot(steps, prices_array, label='Computed Prices')
# plt.axhline(y=bs_price, color='r', linestyle='--', label=f'BS Price: {round(bs_price,2)}')
# plt.title('Price vs Steps')
# plt.xlabel('Steps')
# plt.ylabel('Price')
# plt.legend()
# plt.tight_layout()
# plt.show()
# # --------- 2ème Graphique: Execution Time vs Steps -----------
# plt.figure(figsize=(12, 5))
# plt.plot(steps, execution_times_array, color='green', label='Execution Time')
# plt.title('Execution Time vs Steps')
# plt.xlabel('Steps')
# plt.ylabel('Execution Time (seconds)')
# plt.legend()
# plt.tight_layout()
# plt.show()

# # --------- 3ème Graphique: Gap (BS Price - Computed Prices) -----------
# plt.figure(figsize=(12, 5))
# plt.plot(steps, gap, color='purple', label='Difference')
# plt.title('Difference (BS Price - Computed Prices) vs Steps')
# plt.xlabel('Steps')
# plt.ylabel('Difference')
# plt.axhline(y=0, color='black', linestyle='--')  # Ligne pour montrer la différence nulle
# plt.legend()
# plt.tight_layout()
# plt.show()

# --------- 4ème Graphique: Gap*Step (BS Price - Computed Prices) -----------
# plt.figure(figsize=(12, 5))
# plt.plot(steps, gap_step, color='orange', label='Difference*Pas')
# plt.title('Difference (BS Price - Computed Prices) vs Steps')
# plt.xlabel('Steps')
# plt.ylabel('Difference')
# plt.axhline(y=0, color='black', linestyle='--')  # Ligne pour montrer la différence nulle
# plt.legend()
# plt.tight_layout()
# plt.show()