from pydantic import BaseModel, computed_field, ConfigDict
from math import exp, sqrt
from node import Node
from options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption
from typing import Union
import matplotlib.pyplot as plt
import networkx as nx
from market import Market
import time

from tqdm import tqdm
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
        return exp(self.option.market.volatility * sqrt(3 * self.time_delta)  )
    
    # Fonction pour générer l'arbre trinomial
    def generate_tree(self):
        # Initialiser la racine avec le prix spot du marché
        self.root_node = Node(price = self.option.market.spot)
        mid_node = self.root_node
        # for i in range(1,self.nb_steps):
        #     mid_node = self._build_next_column(mid_node)

        for _ in tqdm(
            range(self.nb_steps-1),
            total=self.nb_steps-1,
            desc="Building tree...",
            leave=False,
        ):
            mid_node = self._build_next_column(mid_node)
    
    def _build_next_column(self, mid_node : Node):
        
        self._build_triplet(mid_node) #On calcule le triplet des noeuds du milieu

         # On va maintenant calculer les noeuds latéraux

        # upper_node = mid_node.up_node  #On calcule les noeuds du haut
        # while upper_node != None:
        #     upper_node = self._compute_upper_nodes(upper_node)

        upper_node = mid_node.up_node  #On calcule les noeuds du haut
        down_node = mid_node.down_node #On calcule les noeuds du bas
        while down_node != None and upper_node !=None:
            upper_node = self._compute_upper_nodes(upper_node)
            down_node = self._compute_down_nodes(down_node)
            


        return mid_node.next_mid


    def _build_triplet(self, node : Node):
        node.next_mid = node.calculate_forward_node(self.option.market.rate, self.time_delta)
        node.next_up = Node(price = node.next_mid.price * self.alpha)
        node.next_down = Node(price = node.next_mid.price / self.alpha)

        node.next_mid.down_node = node.next_down
        node.next_mid.up_node = node.next_up

        node.next_up.down_node = node.next_mid
        node.next_down.up_node = node.next_mid

        node.next_mid.prec_node = node #On construit le noeud précédent afin de simplifier le pricing

    def _compute_upper_nodes(self,upper_node):
        upper_node.next_mid = upper_node.down_node.next_up
        upper_node.next_down = upper_node.down_node.next_mid
        next_up_price = upper_node.next_mid.price * self.alpha
        upper_node.next_up = Node(price = next_up_price)

        upper_node.next_up.down_node = upper_node.next_mid
        upper_node.next_mid.up_node = upper_node.next_up

        return upper_node.up_node

    def _compute_down_nodes(self, down_node):
        down_node.next_mid = down_node.up_node.next_down
        down_node.next_up = down_node.up_node.next_mid
        next_down_price = down_node.next_mid.price / self.alpha
        down_node.next_down = Node(price = next_down_price)

        down_node.next_down.up_node = down_node.next_mid
        down_node.next_mid.down_node = down_node.next_down

        return down_node.down_node
    
    def visualize_tree(self):
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

        # Ajouter les noeuds de l'arbre à partir de la racine
        add_edges_by_level(self.root_node, 0)

        # Tracer le graphe
        plt.figure(figsize=(15, 10))
        nx.draw(G, pos, labels=node_labels, with_labels=True, node_size=1000, node_color="lightblue", font_size=8, font_color="black", font_weight='bold', arrowsize=10)
        plt.title("Arbre Trinomial - Visualisation 2D Optimisée (Prix uniquement)")
        plt.show()


    
if __name__ == "__main__":
    # Paramètres d'exemple
    spot = 100           # Prix initial
    rate = 0.05          # Taux d'intérêt
    volatility = 0.2     # Volatilité du marché
    time_to_maturity = 1  # Temps jusqu'à la maturité (1 an)
    nb_steps = 1000    # Nombre d'étapes dans l'arbre

    start=time.time()
    # Créer le marché et l'option
    market = Market(spot=spot, rate=rate, volatility=volatility)
    option = EuropeanCallOption(market=market, time_to_maturity=time_to_maturity,strike=105)

    # Initialiser l'arbre trinomial
    tree = Tree(option=option, nb_steps=nb_steps)

    # Générer l'arbre
    tree.generate_tree()
    print(time.time()-start)

    #tree.visualize_tree()