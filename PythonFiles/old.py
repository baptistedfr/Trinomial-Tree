def _find_mid_down(self, node : Node, candidate_mid : Node) -> Node:
    """Returns the next mid which is the closest to the forward price for down nodes computation"""

    forward_value = node.price * exp(self.market.rate * self.time_delta) - self.market.dividende

    while(True):
        down_price = candidate_mid.price / self.alpha

        average_price = (candidate_mid.price + down_price) / 2

        if forward_value > average_price:
            return candidate_mid
        else:
            future_mid_node = Node(price = down_price)
            future_mid_node.up_node = candidate_mid
            candidate_mid.down_node = future_mid_node

            candidate_mid = future_mid_node

def _find_mid_up(self, node : Node, candidate_mid : Node) -> Node:
    """Returns the next mid which is the closest to the forward price for upper nodes computation"""

    forward_value = node.price * exp(self.market.rate * self.time_delta) - self.market.dividende

    while(True):
        up_price = candidate_mid.price * self.alpha

        average_price = (candidate_mid.price + up_price) / 2

        if forward_value < average_price:
            return candidate_mid
        else:
            future_mid_node = Node(price = up_price)
            future_mid_node.down_node = candidate_mid
            candidate_mid.up_node = future_mid_node

            candidate_mid = future_mid_node

import xlwings as xw
from PythonFiles.options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption
from PythonFiles.market import Market
from PythonFiles.tree import Tree
from datetime import datetime
from abc import ABC,abstractmethod
from math import log,sqrt,exp,floor
from re import T
from scipy.stats import norm
import time


@xw.func
def test_xl(name):
    return "Hello " + name

# def main():
#     wb = xw.Book.caller()
#     sheet = wb.sheets[0]
#     if sheet["A1"].value == "Hello xlwings!":
#         sheet["A1"].value = "Bye xlwings!"
#     else:
#         sheet["A1"].value = "Hello xlwings!"
# def main():
    
#     wb = xw.Book.caller()
#     sheet_pricer = wb.sheets["Pricer"]

#     # Paramètres du marché
#     initial_price: float = sheet_pricer.range('IntialPrice').value
#     volatility: float = sheet_pricer.range('Volatility').value
#     risk_free_rate: float = sheet_pricer.range('InterestRate').value
#     dividende: float = sheet_pricer.range('Dividend').value
#     if (dividende >0):
#         div_date: datetime = sheet_pricer.range('DivDate').value
#         market = Market(spot=initial_price, volatility=volatility, rate=risk_free_rate, dividende=dividende, div_date=div_date)
#     else:
#         market = Market(spot=initial_price, volatility=volatility, rate=risk_free_rate, dividende=dividende)


#     # Paramètres de l'option
#     type_option: str = sheet_pricer.range('OptionType').value
#     exercise_type: float = sheet_pricer.range('ExerciceType').value
#     strike: float = sheet_pricer.range('Strike').value
#     maturity: float = sheet_pricer.range('Maturity').value
#     start_date: datetime = sheet_pricer.range('StartDate').value

#     option_class_name = f"{exercise_type}{type_option}Option"
#     option_class = globals().get(option_class_name)
#     if option_class: #Liste des dates non prises en compte pour l'instant pour les bermudéennes
#         option = option_class(market=market, strike=strike, time_to_maturity=maturity, start_date=start_date)
#     else:
#         raise ValueError(f"Classe d'option {option_class_name} non trouvée dans le module PythonFiles.options.")

#     # Paramètres du tree
#     nb_steps: int = int(sheet_pricer.range('NbSteps').value)

#     # On instance l'abre
#     start_time = time.time()
#     tree = Tree(option=option, nb_steps=nb_steps)
#     print(f"Number of steps : {nb_steps}")

#     start=time.time()
#     tree.generate_tree()
#     tree.price()
#     tree_time = time.time() - start
#     sheet_pricer.range('TreePricePython').value = tree.root_node.payoff
#     sheet_pricer.range('TreeTimePython').value = tree_time

#     start=time.time()
#     bs_price = option.compute_price()
#     bs_time = time.time() - start
#     sheet_pricer.range('BSPricePython').value = bs_price
#     sheet_pricer.range('BSTimePython').value = bs_time
    

def main():
    try:
        # Si le script est exécuté depuis Excel
        wb = xw.Book.caller()
    except:
        # Si le script est exécuté directement depuis Python (par exemple via un terminal ou un IDE)
        wb = xw.Book("PricingOptions.xlsm")  # Remplacez par le chemin correct si nécessaire
    
    # Accéder à la première feuille
    sheet = wb.sheets[0]
    if sheet["A1"].value == "Hello xlwings!":
        sheet["A1"].value = "Bye xlwings!"
    else:
        sheet["A1"].value = "Hello xlwings!"