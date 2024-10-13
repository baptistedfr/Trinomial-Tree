import xlwings as xw
import time
import numpy as np
import matplotlib.pyplot as plt
from PythonFiles.market import Market
from PythonFiles.options import Option, EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption
from PythonFiles.tree import Tree
from PricingOptions import make_market_from_input, make_option_from_input, make_tree_from_input
from main import analyse
from PythonFiles.visualisation import price_convergence, plot_execution_time, plot_gap, plot_gap_step
    
@xw.sub
def PythonPrice():
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
    prices = []
    execution_times = []
    
    #Boucle sur chaque valeur de la plage
    for step in steps:
        tree = Tree(market = mkt, option=option, nb_steps=int(step), prunning_value=1e-10)
        start=time.time()
        tree.generate_tree()
        tree.price()
        temps_exec = round(time.time()-start,5)

        prices.append(tree.root_node.payoff)          # Ajoute le prix au vecteur
        execution_times.append(temps_exec)  # Ajoute le temps d'exécution au vecteur

    # Convertir les listes en tableaux NumPy si nécessaire
    prices_array = np.array(prices)
    execution_times_array = np.array(execution_times)
    bs_price = option.compute_price(mkt)
    gap = bs_price - prices_array
    gap_step = gap * steps

    # --------- Génération des graphs -----------
    fig_conv = price_convergence(steps, prices_array, bs_price)
    fig_time = plot_execution_time(steps, execution_times_array)
    fig_gap = plot_gap(steps, gap)
    fig_gap_step = plot_gap_step(steps, gap_step)
    
    sheet_conv.pictures.add(fig_conv, name='ConvPlot', update=True, left=sheet_conv.range('H36').left, top=sheet_conv.range('H36').top)
    sheet_conv.pictures.add(fig_time, name='TimePlot', update=True, left=sheet_conv.range('P36').left, top=sheet_conv.range('P36').top)
    sheet_conv.pictures.add(fig_gap, name='GapPlot', update=True, left=sheet_conv.range('H49').left, top=sheet_conv.range('H49').top)
    sheet_conv.pictures.add(fig_gap_step, name='GapStepPlot', update=True, left=sheet_conv.range('P49').left, top=sheet_conv.range('P49').top)
    

    