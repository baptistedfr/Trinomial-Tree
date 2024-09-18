from pydantic import BaseModel, computed_field, ConfigDict
from math import exp, sqrt
from node import Node
from options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption
from typing import Union
import matplotlib.pyplot as plt
import networkx as nx
from market import Market

class Tree(BaseModel):
   
     option : Union[EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption]
     nb_steps : int
     root_node : Node = None
     
     
     @computed_field
     @property
     def time_delta(self) -> float:
          return self.option.time_to_maturity / self.nb_steps    
     
     @computed_field
     @property
     def alpha(self) -> float:
          return exp(self.option.market.volatility * sqrt(3 * self.time_delta))

     # Fonction pour générer l'arbre trinomial
     def generate_tree(self):
        # Initialiser la racine avec le prix spot du marché
        self.root_node = Node(price = self.option.market.spot)
        # Construire l'arbre récursivement à partir de la racine
        self.build_triplet(self.root_node, current_step=1)


     def build_triplet(self, node : Node, current_step : int, position_from : str = "mid"):
        # Condition d'arrêt : si on a atteint le dernier niveau, on retourne
        if current_step >= self.nb_steps:
            return


        next_mid_price = node.price * exp(self.option.market.rate * self.time_delta)
        if position_from == "mid":
            node.next_mid = Node(price = next_mid_price)
            node.next_up = Node(price = next_mid_price * self.alpha)
            node.next_down = Node(price = next_mid_price / self.alpha)

        elif position_from == "up":
            node.next_mid = node.down_node.next_up #Si c est un noeud du haut alors le milieu est le noeud haut du noeud milieu précédent
            node.next_up = Node(price = next_mid_price * self.alpha)
            node.next_down = node.down_node.next_mid # Le bas du haut equivaut au milieu du milieu précédent
            
        elif position_from == "down":
            node.next_mid = node.up_node.next_down #Si c est un noeud du bas alors le milieu est le noeud bas du noeud milieu précédent
            node.next_up = node.up_node.next_mid # Le haut du bas correspond au milieu du milieu
            node.next_down = Node(price = next_mid_price / self.alpha) 
        
        node.next_up.down_node = node.next_mid
        node.next_down.up_node = node.next_mid
        a=0
        # Appel récursif pour construire les sous-arbres à partir de chaque enfant
        self.build_triplet(node = node.next_mid, current_step=current_step + 1, position_from="mid")
        self.build_triplet(node = node.next_up, current_step=current_step + 1, position_from="up")
        self.build_triplet(node = node.next_down, current_step=current_step + 1, position_from="down")

     # Fonction pour visualiser l'arbre
     # Nouvelle fonction de tracé
     # Visualisation de l'arbre avec NetworkX
     
     def plot_tree_hierarchical(self,root):
        G = nx.DiGraph()
        labels = {}

        def add_edges(node, level=0, pos='mid', parent=None):
            if node is None:
                return
            node_id = f"{level}-{pos}-{node.price:.2f}"
            labels[node_id] = f"{node.price:.2f}"
            if parent is not None:
                G.add_edge(parent, node_id)

            add_edges(node.next_mid, level + 1, 'mid', node_id)
            add_edges(node.next_up, level + 1, 'up', node_id)
            add_edges(node.next_down, level + 1, 'down', node_id)

        add_edges(root)

        # Utiliser spring_layout comme alternative
        pos = nx.spring_layout(G, seed=42)  # Seed pour la reproductibilité

        nx.draw(G, pos, with_labels=True, labels=labels, node_size=3000, node_color="lightgreen", font_size=10, font_weight='bold', arrows=True)
        plt.show()

if __name__ == "__main__":
    # Paramètres d'exemple
    spot = 100           # Prix initial
    rate = 0.05          # Taux d'intérêt
    volatility = 0.2     # Volatilité du marché
    time_to_maturity = 1  # Temps jusqu'à la maturité (1 an)
    nb_steps = 3         # Nombre d'étapes dans l'arbre


    # Créer le marché et l'option
    market = Market(spot=spot, rate=rate, volatility=volatility)
    option = EuropeanCallOption(market=market, time_to_maturity=time_to_maturity,strike=105)

    # Initialiser l'arbre trinomial
    tree = Tree(option=option, nb_steps=nb_steps)

    # Générer l'arbre
    tree.generate_tree()

    # Visualiser l'arbre
    tree.plot_tree_hierarchical(tree.root_node)  