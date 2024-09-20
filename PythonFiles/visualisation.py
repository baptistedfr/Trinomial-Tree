import matplotlib.pyplot as plt
from tree import Tree
import networkx as nx

def visualize_tree(tree : Tree):
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
        add_edges_by_level(tree.root_node, 0)

        # Tracer le graphe
        plt.figure(figsize=(15, 10))
        nx.draw(G, pos, labels=node_labels, with_labels=True, node_size=1000, node_color="lightblue", font_size=8, font_color="black", font_weight='bold', arrowsize=10)
        plt.title("Arbre Trinomial - Visualisation 2D Optimisée (Prix uniquement)")
        plt.show()