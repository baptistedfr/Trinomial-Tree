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

def main():
    
    wb = xw.Book.caller()
    sheet_pricer = wb.sheets["Pricer"]

    # Paramètres du marché
    initial_price: float = sheet_pricer.range('IntialPrice').value
    volatility: float = sheet_pricer.range('Volatility').value
    risk_free_rate: float = sheet_pricer.range('InterestRate').value
    dividende: float = sheet_pricer.range('Dividend').value
    if (dividende >0):
        div_date: datetime = sheet_pricer.range('DivDate').value
        market = Market(spot=initial_price, volatility=volatility, rate=risk_free_rate, dividende=dividende, div_date=div_date)
    else:
        market = Market(spot=initial_price, volatility=volatility, rate=risk_free_rate, dividende=dividende)


    # Paramètres de l'option
    type_option: str = sheet_pricer.range('OptionType').value
    exercise_type: float = sheet_pricer.range('ExerciceType').value
    strike: float = sheet_pricer.range('Strike').value
    maturity: float = sheet_pricer.range('Maturity').value
    start_date: datetime = sheet_pricer.range('StartDate').value

    option_class_name = f"{exercise_type}{type_option}Option"
    option_class = globals().get(option_class_name)
    if option_class: #Liste des dates non prises en compte pour l'instant pour les bermudéennes
        option = option_class(market=market, strike=strike, time_to_maturity=maturity, start_date=start_date)
    else:
        raise ValueError(f"Classe d'option {option_class_name} non trouvée dans le module PythonFiles.options.")

    # Paramètres du tree
    nb_steps: float = sheet_pricer.range('NbSteps').value

    # On instance l'abre
    start_time = time.time()
    tree = Tree(option=option, nb_steps=nb_steps)
    print(f"Number of steps : {nb_steps}")

    start=time.time()
    tree.generate_tree()
    tree.price()
    tree_time = time.time() - start
    sheet_pricer.range('TreePricePython').value = tree.root_node.payoff
    sheet_pricer.range('TreeTimePython').value = tree_time

    start=time.time()
    bs_price = option.compute_price()
    bs_time = time.time() - start
    sheet_pricer.range('BSPricePython').value = bs_price
    sheet_pricer.range('BSTimePython').value = bs_time
    
if __name__ == "__main__":
    xw.Book("PricingOptions.xlsm").set_mock_caller()
    main()