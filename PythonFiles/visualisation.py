import matplotlib.pyplot as plt
import plotly.graph_objects as go
import networkx as nx
from PythonFiles.tree import Tree

def visualize_tree(tree : Tree, nb_steps):
    G = nx.DiGraph()  # Utilisation d'un graphe dirigé pour respecter la hiérarchie
    node_labels = {}
    pos = {}
    # Ajout des noeuds et des arêtes par niveau
    def add_edges_by_level(node, level=0, parent=None, pos_y=0):
        if node is None:
            return
        # Création d'un label pour le noeud avec seulement le prix (sans "up", "mid", "down")
        node_label = f"{round(node.price, 2)}"
        node_id = f"{level}_{round(node.price, 2)}"
        node_labels[node_id] = node_label

        # Ajout du noeud et de l'arête avec le parent
        G.add_node(node_id, level=level)
        if parent:
            G.add_edge(parent, node_id)

        # Définir la position du noeud en 2D (x=level, y=pos_y)
        pos[node_id] = (level, pos_y)
        # Appel récursif pour les noeuds enfants
        add_edges_by_level(node.next_up, level+1, node_id, pos_y+1)
        add_edges_by_level(node.next_mid, level+1, node_id, pos_y)
        add_edges_by_level(node.next_down, level+1, node_id, pos_y-1)

    add_edges_by_level(tree.root_node, 0)
    fig = plt.figure(figsize=(15, 10))
    nx.draw(G, pos, labels=node_labels, with_labels=True, node_size=1000, node_color="lightblue", font_size=8, font_color="black", font_weight='bold', arrowsize=10)
    plt.title("Arbre Trinomial - Visualisation 2D Optimisée (Prix uniquement)")
    return fig

def plot_price_convergence(steps, prices_array, bs_price):
    fig, ax = plt.subplots()  
    ax.plot(steps, prices_array, label='Computed Prices')
    ax.axhline(y=bs_price, color='r', linestyle='--', label=f'BS Price: {round(bs_price, 2)}')
    ax.set_title('Price convergence towards Black-Scholes')
    ax.set_xlabel('Steps')
    ax.set_ylabel('Price €')
    ax.legend()
    plt.tight_layout()
    return fig  

def plot_execution_time(steps, execution_time):
    fig, ax = plt.subplots(figsize=(12, 5)) 
    ax.plot(steps, execution_time, color='green', label='Execution Time')  
    ax.set_title('Execution Time vs Steps')
    ax.set_xlabel('Steps')
    ax.set_ylabel('Execution Time (seconds)')
    ax.legend()
    plt.tight_layout()
    return fig  

def plot_gap(steps, gap):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(steps, gap, color='purple', label='Difference (BS Price - Computed Prices)')
    ax.set_title('Difference (BS Price - Computed Prices) vs Steps')
    ax.set_xlabel('Steps')
    ax.set_ylabel('Difference')
    ax.axhline(y=0, color='black', linestyle='--') 
    ax.legend()
    plt.tight_layout()
    return fig  

def plot_gap_step(steps, gap_step):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(steps, gap_step, color='orange', label='Difference * Step')
    ax.set_title('Difference (BS Price - Computed Prices) * Steps vs Steps')
    ax.set_xlabel('Steps')
    ax.set_ylabel('Difference * Step')
    ax.axhline(y=0, color='black', linestyle='--')  
    ax.legend()
    plt.tight_layout()
    return fig 