from PythonFiles.options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption
from PythonFiles.visualisation import visualize_tree
from datetime import datetime
from PythonFiles.market import Market
from PythonFiles.tree import Tree
import time

nb_steps = 500
market = Market(spot=100, rate=0.05, volatility=0.2,div_date=datetime(2024,2,1), dividende=2)
option = EuropeanPutOption(market=market, time_to_maturity=1, strike=105, start_date=datetime(2024,1,1))
# option = AmericanPutOption(market=market, time_to_maturity=1, strike=105, start_date=datetime(2024,1,1), div_date=datetime(2024,2,1), dividende=0)
# option = BermudeanPutOption(market=market, time_to_maturity=1, strike=105, start_date=datetime(2024,1,1), div_date=datetime(2024,2,1), dividende=0, exercise_dates=[datetime(2024,4,1), datetime(2024,8,1)])
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
    print(f"Option price with B&S (or MC): {option.compute_price()}")
    
    if visualise:
        visualize_tree(tree)

generate_and_price(False)
print("End")