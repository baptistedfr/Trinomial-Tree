import xlwings as xw
import numpy as np
import time
import os
import matplotlib.pyplot as plt
from PythonFiles.market import Market
from PythonFiles.tree import Tree
from PythonFiles.utils import make_market_from_input, make_option_from_input, make_tree_from_input, calculate_prices_range
from PythonFiles.visualisation import plot_price_convergence, plot_execution_time, plot_gap, plot_gap_step

def main():
    '''
    Permet de calculer le prix de l'option avec arbre trinomial depuis python en prenant les paramètres excels
    '''
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

@xw.sub
def PythonPrice():
    '''
    Création d'un sub excel avec xlwings permettant de calculer un prix en utilisant le script python depuis xlwings
    '''
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

@xw.sub
def generate_python_graphs():
    '''
    Création d'un sub excel avec xlwings permettant de générer les graphs en utilisant le script python depuis xlwings
    '''
    try:
        # Si le script est exécuté depuis Excel
        wb = xw.Book.caller()
    except:
        # Si le script est exécuté directement depuis Python (par exemple via un terminal ou un IDE)
        wb = xw.Book("PricingOptions.xlsm")  # Remplacez par le chemin correct si nécessaire
    
    # Accéder à la première feuille
    sheet_pricer = wb.sheets["Interface"]
    sheet_conv = wb.sheets["Convergence Study"]
    
    # Initialisation des classes
    mkt = make_market_from_input(sheet_pricer)
    option = make_option_from_input(sheet_pricer)
    steps = sheet_conv.range('StepRange').options(np.ndarray).value
    prices,execution_times = calculate_prices_range(steps, mkt, option)

    bs_price = option.compute_price(mkt)
    gap = bs_price - prices
    gap_step = gap * steps

    # --------- Génération des graphs -----------
    fig_conv = plot_price_convergence(steps, prices, bs_price)
    fig_time = plot_execution_time(steps, execution_times)
    fig_gap = plot_gap(steps, gap)
    fig_gap_step = plot_gap_step(steps, gap_step)
    
    sheet_conv.pictures.add(fig_conv, name='Picture 1', update=True)
    sheet_conv.pictures.add(fig_time, name='Picture 2', update=True)
    sheet_conv.pictures.add(fig_gap, name='Picture 7', update=True)
    sheet_conv.pictures.add(fig_gap_step, name='Picture 8', update = True)
    
if __name__ == "__main__":
    #main()
    generate_python_graphs()
    

