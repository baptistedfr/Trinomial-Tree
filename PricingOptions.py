import xlwings as xw
from datetime import datetime
from abc import ABC,abstractmethod
from math import log,sqrt,exp,floor
from re import T
from scipy.stats import norm
import time
from PythonFiles.options import Option, EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption
from PythonFiles.market import Market
from PythonFiles.tree import Tree


def make_market_from_input(sheet) -> Market:
    '''
    Fonction permettant de créer un marché depuis les paramètres de la feuille
    '''
    spot: float = sheet.range('ISpot').value
    volatility: float = sheet.range('IVol').value
    risk_free_rate: float = sheet.range('IRate').value
    dividende: float = sheet.range('IDiv').value
    div_date: datetime = sheet.range('IDivDate').value
    market = Market(spot=spot, volatility=volatility, rate=risk_free_rate, dividende=dividende, div_date=div_date)
    return market

def make_option_from_input(sheet) -> Option:
    # Paramètres de l'option
    start_date: datetime = sheet.range('IStartDate').value
    maturity: float = sheet.range('IMaturity').value
    strike: float = sheet.range('IStrike').value
    option_type: str = sheet.range('IOptionType').value
    exercise: float = sheet.range('IExerciseType').value
    match (exercise):
        case "European":
                if option_type == "Call":
                    option = EuropeanCallOption(time_to_maturity=maturity, strike=strike, start_date=start_date)
                else:
                    option = EuropeanPutOption(time_to_maturity=maturity, strike=strike, start_date=start_date)
        case "American":
            if option_type == "Call":
                option = AmericanCallOption(time_to_maturity=maturity, strike=strike, start_date=start_date)
            else:
                option = AmericanPutOption(time_to_maturity=maturity, strike=strike, start_date=start_date)
    return option

def make_tree_from_input(sheet, mkt:Market, opt:Option, nb_steps:int = 0) -> Tree:
    '''
    Fonction permettant de créer un marché depuis les paramètres de la feuille ou avec un step en particulier
    '''
    if(nb_steps==0):
        nb_steps: int = int(sheet.range('INbSteps').value)
    prunning : float = sheet.range('IPrunning').value
    return Tree(option = opt, market = mkt, nb_steps = nb_steps, prunning_value = prunning)

def main():
    try:
        # Si le script est exécuté depuis Excel
        wb = xw.Book.caller()
    except:
        # Si le script est exécuté directement depuis Python (par exemple via un terminal ou un IDE)
        wb = xw.Book("PricingOptions.xlsm")  # Remplacez par le chemin correct si nécessaire
    
    # Accéder à la première feuille
    sheet_pricer = wb.sheets["Interface"]
    # Initialisation des classes
    mkt = make_market_from_input(sheet_pricer)
    option = make_option_from_input(sheet_pricer)
    tree = make_tree_from_input(sheet_pricer, mkt, option)

    start=time.time()
    tree.generate_tree()
    generate_time = time.time() - start

    start=time.time()
    tree.price()
    price_time = time.time() - start

    sheet_pricer.range('IPythonPrice').value = tree.root_node.payoff
    sheet_pricer.range('IPythonTimeTree').value = generate_time
    sheet_pricer.range('IPythonPriceTime').value = price_time


    
if __name__ == "__main__":
    main()
    

