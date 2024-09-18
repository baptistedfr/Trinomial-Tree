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
     
     model_config = ConfigDict(arbitrary_types_allowed=True)
     
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


     def build_triplet(self, node, current_step):
        # Condition d'arrêt : si on a atteint le dernier niveau, on retourne
        if current_step >= self.nb_steps:
            return

        # Calcul des prix pour les nœuds "mid", "up" et "down"
        next_mid_price = node.price * exp(self.option.market.rate * self.time_delta)
        node.next_mid = Node(price = next_mid_price)
        node.next_up = Node(price = next_mid_price * self.alpha)
        node.next_down = Node(price = next_mid_price / self.alpha)

        print(f"STEP : {current_step} {node.price} Next Mid {node.next_mid.price} Next up {node.next_up.price} next Down {node.next_down.price}" )
        # Connecter les enfants entre eux
        node.next_mid.down_node = node.next_down
        node.next_mid.up_node = node.next_up
        node.next_up.down_node = node.next_mid
        node.next_down.up_node = node.next_mid

        # Appel récursif pour construire les sous-arbres à partir de chaque enfant
        self.build_triplet(node = node.next_up, current_step=current_step + 1)
        self.build_triplet(node = node.next_mid, current_step=current_step + 1)
        self.build_triplet(node = node.next_down, current_step=current_step + 1)
     # Fonction pour visualiser l'arbre
     # Nouvelle fonction de tracé
     def plot_tree(self):
        import matplotlib.pyplot as plt
        import networkx as nx

        G = nx.DiGraph()  # Créer un graphe orienté
        pos = {}  # Stockage des positions des nœuds pour le tracé
        labels = {}  # Stockage des labels des nœuds (prix) pour les afficher

        def traverse_and_add_edges(node, x, y, level=0):
            if node is None:
                return

            # Ajouter le nœud au graphe avec sa position
            G.add_node((x, y), label=f'{node.price:.2f}')
            pos[(x, y)] = (x, -y)
            labels[(x, y)] = f'{node.price:.2f}'

            offset = 2 ** (-level)  # Décalage horizontal pour espacer les nœuds

            if node.next_up:
                G.add_edge((x, y), (x + offset, y + 1))
                traverse_and_add_edges(node.next_up, x + offset, y + 1, level + 1)

            if node.next_mid:
                G.add_edge((x, y), (x, y + 1))
                traverse_and_add_edges(node.next_mid, x, y + 1, level + 1)

            if node.next_down:
                G.add_edge((x, y), (x - offset, y + 1))
                traverse_and_add_edges(node.next_down, x - offset, y + 1, level + 1)

        # Commence par la racine
        traverse_and_add_edges(self.root_node, x=0, y=0)

        # Tracer le graphe
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, labels=labels, node_size=2000, node_color="lightblue", font_size=10,
                font_weight="bold", arrows=False)
        plt.title("Visualisation de l'arbre trinomial avec les prix")
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
    tree.plot_tree()  