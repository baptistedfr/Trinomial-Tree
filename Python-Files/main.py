from market import Market
from options import EuropeanCallOption
from visualisation import visualize_tree
from datetime import datetime
from tree import Tree
import time

nb_steps = 1000
market = Market(spot=100, rate=0.05, volatility=0.2)
# option = EuropeanCallOption(market=market, time_to_maturity=1, strike=105)
option = EuropeanCallOption(market=market, time_to_maturity=1, strike=105, start_date=datetime(2024,1,1), div_date=datetime(2024,2,1), dividende=3)
tree = Tree(option=option, nb_steps=nb_steps)

def generate_and_price(visualise : bool = False):

    print(f"Number of steps : {nb_steps}")

    start=time.time()
    tree.generate_tree()
    print(f"Tree generated in : {round(time.time()-start,5)} sec")

    start=time.time()
    tree.price()
    print(f"Option priced in : {round(time.time()-start,5)} sec")

    print(f"Option price with tree : {tree.root_node.payoff}")
    print(f"Option price with B&S: {option.compute_BS()}")
    
    if visualise:
        visualize_tree(tree)

generate_and_price()
print("End")