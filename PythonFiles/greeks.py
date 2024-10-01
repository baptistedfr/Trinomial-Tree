from PythonFiles.market import Market
from PythonFiles.tree import Tree
import copy

def compute_delta(tree : Tree, market : Market, option, nb_steps, prunning_value):
    delta_s = market.spot * 0.01

    market_bis = Market(market.spot + delta_s, rate=market.rate, volatility=market.volatility, div_date=market.div_date, dividende=market.dividende)
    tree_bis = Tree(market=market_bis, option=option, nb_steps=nb_steps, prunning_value=prunning_value)
    tree_bis.generate_tree()
    tree_bis.price()

    return (tree_bis.root_node.payoff - tree.root_node.payoff)/(delta_s)

def compute_vega(tree : Tree, market : Market, option, nb_steps, prunning_value):
    delta_v = market.volatility * 0.01

    market_bis = Market(market.spot, rate=market.rate, volatility=market.volatility + delta_v, div_date=market.div_date, dividende=market.dividende)
    tree_bis = Tree(market=market_bis, option=option, nb_steps=nb_steps, prunning_value=prunning_value)
    tree_bis.generate_tree()
    tree_bis.price()

    return (tree_bis.root_node.payoff - tree.root_node.payoff)/(delta_v)
    
def compute_gamma(tree : Tree, market : Market, option, nb_steps, prunning_value):
    delta_s = market.spot * 0.01

    market_bis = Market(market.spot + delta_s, rate=market.rate, volatility=market.volatility, div_date=market.div_date, dividende=market.dividende)
    tree_bis = Tree(market=market_bis, option=option, nb_steps=nb_steps, prunning_value=prunning_value)
    tree_bis.generate_tree()
    tree_bis.price()

    market_ter = Market(market.spot - delta_s, rate=market.rate, volatility=market.volatility, div_date=market.div_date, dividende=market.dividende)
    tree_ter = Tree(market=market_ter, option=option, nb_steps=nb_steps, prunning_value=prunning_value)
    tree_ter.generate_tree()
    tree_ter.price()

    return (tree_bis.root_node.payoff - 2*tree.root_node.payoff + tree_ter.root_node.payoff)/(delta_s)**2

def compute_theta(tree : Tree, market : Market, option, nb_steps, prunning_value):
    delta_t = option.time_to_maturity * 0.01
    option_bis = copy.deepcopy(option)
    option_bis.time_to_maturity = option.time_to_maturity + delta_t

    tree_bis = Tree(market=market, option=option_bis, nb_steps=nb_steps, prunning_value=prunning_value)
    tree_bis.generate_tree()
    tree_bis.price()

    return (tree_bis.root_node.payoff - tree.root_node.payoff)/(delta_t)

def compute_rho(tree : Tree, market : Market, option, nb_steps, prunning_value):
    delta_r = market.rate * 0.01

    market_bis = Market(market.spot, rate=market.rate + delta_r, volatility=market.volatility, div_date=market.div_date, dividende=market.dividende)
    tree_bis = Tree(market=market_bis, option=option, nb_steps=nb_steps, prunning_value=prunning_value)
    tree_bis.generate_tree()
    tree_bis.price()

    return (tree_bis.root_node.payoff - tree.root_node.payoff)/(delta_r)

def compute_greeks(tree : Tree, market : Market, option, nb_steps, prunning_value):
    
    delta = compute_delta(tree, market, option, nb_steps, prunning_value)
    vega = compute_vega(tree , market , option, nb_steps, prunning_value)
    gamma = compute_gamma(tree , market , option, nb_steps, prunning_value)
    theta = compute_theta(tree , market , option, nb_steps, prunning_value)
    rho = compute_rho(tree , market , option, nb_steps, prunning_value)

    print("\nGreeks : ")
    print(f"Delta : {round(delta,3)}")
    print(f"Gamma : {round(gamma,3)}")
    print(f"Vega : {round(vega,3)}")
    print(f"Theta : {round(theta,3)}")
    print(f"Rho : {round(rho,3)}")