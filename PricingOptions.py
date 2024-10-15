import xlwings as xw
import numpy as np
import pandas as pd
import time
from tqdm import tqdm
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from PythonFiles.tree import Tree
from PythonFiles.greeks import compute_greeks
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

@xw.sub
def generate_greeks_graphs():
    '''
    Création d'un sub excel avec xlwings permettant de générer les graphs en utilisant le script python depuis xlwings
    '''
    try:
        # Si le script est exécuté depuis Excel
        wb = xw.Book.caller()
    except:
        # Si le script est exécuté directement depuis Python (par exemple via un terminal ou un IDE)
        wb = xw.Book("PricingOptions.xlsm")  # Remplacez par le chemin correct si nécessaire
    sheet_pricer = wb.sheets["Interface"]
    #sheet_greeks = wb.sheets["Greeks"]
    # Initialisation des classes
    greeks = []
    opt = make_option_from_input(sheet_pricer)
    spots = np.arange(int(opt.strike/2), int(opt.strike*1.5), 0.5 * int(opt.strike/100))
    for spot in tqdm(spots):
        mkt = make_market_from_input(sheet_pricer, spot)
        tree = Tree(opt, mkt, nb_steps = 200, prunning_value = 10^-7)
        tree.generate_tree()
        tree.price()
        greek_values = compute_greeks(tree, mkt, opt, 200, 10**-7)
        greeks.append(greek_values)
    df_greeks = pd.DataFrame(greeks)
    df_greeks['Spot'] = spots

    # Tracer Delta
    fig_delta = go.Figure()
    fig_delta.add_trace(go.Scatter(x=df_greeks['Spot'], y=df_greeks['Delta'], mode='lines+markers', name='Delta', line=dict(color='blue')))
    fig_delta.update_layout(title='Variation de Delta en fonction du Spot',
                            xaxis_title='Spot',
                            yaxis_title='Delta',
                            template='plotly_white')
    fig_delta.show()

    # Tracer Gamma
    fig_gamma = go.Figure()
    fig_gamma.add_trace(go.Scatter(x=df_greeks['Spot'], y=df_greeks['Gamma'], mode='lines+markers', name='Gamma', line=dict(color='green')))
    fig_gamma.update_layout(title='Variation de Gamma en fonction du Spot',
                            xaxis_title='Spot',
                            yaxis_title='Gamma',
                            template='plotly_white')
    fig_gamma.show()

    # Tracer Vega
    fig_vega = go.Figure()
    fig_vega.add_trace(go.Scatter(x=df_greeks['Spot'], y=df_greeks['Vega'], mode='lines+markers', name='Vega', line=dict(color='red')))
    fig_vega.update_layout(title='Variation de Vega en fonction du Spot',
                        xaxis_title='Spot',
                        yaxis_title='Vega',
                        template='plotly_white')
    fig_vega.show()

    # Tracer Theta
    fig_theta = go.Figure()
    fig_theta.add_trace(go.Scatter(x=df_greeks['Spot'], y=df_greeks['Theta'], mode='lines+markers', name='Theta', line=dict(color='purple')))
    fig_theta.update_layout(title='Variation de Theta en fonction du Spot',
                            xaxis_title='Spot',
                            yaxis_title='Theta',
                            template='plotly_white')
    fig_theta.show()

    # Tracer Rho
    fig_rho = go.Figure()
    fig_rho.add_trace(go.Scatter(x=df_greeks['Spot'], y=df_greeks['Rho'], mode='lines+markers', name='Rho', line=dict(color='orange')))
    fig_rho.update_layout(title='Variation de Rho en fonction du Spot',
                        xaxis_title='Spot',
                        yaxis_title='Rho',
                        template='plotly_white')
    fig_rho.show()
if __name__ == "__main__":
    #main()
    generate_greeks_graphs()
    

