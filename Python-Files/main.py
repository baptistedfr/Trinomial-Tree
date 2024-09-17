from market import Market
from options import EuropeanCallOption
from datetime import datetime
from tree import Tree

new_market = Market(spot=100, volatility=0.20, rate=0.05, dividende=3, div_date=datetime(2024,1,10))
eu_opt = EuropeanCallOption(strike=100, time_to_maturity=1, start_date=datetime(2024,1,1), market=new_market)
tree = Tree(option=eu_opt, nb_steps=1)
tree.build_tree()
print(tree.root_node.price)
print(tree.root_node.next_up.price)
print(tree.root_node.next_mid.price)
print(tree.root_node.next_down.price)