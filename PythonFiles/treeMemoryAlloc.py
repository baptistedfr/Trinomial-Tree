from PythonFiles.options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption
from math import exp, sqrt, ceil
from typing import Union
from PythonFiles.node import Node
from tqdm import tqdm
from dataclasses import dataclass
from functools import cached_property
from PythonFiles.market import Market

@dataclass
class TreeMemoryAlloc():
   
    option : Union[EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption]
    market : Market
    nb_steps : int
    root_node : Node = None
    prunning_value : float = None

    @cached_property
    def time_delta(self) -> float:
        return self.option.time_to_maturity / self.nb_steps    

    @cached_property
    def alpha(self) -> float:
        return exp(self.market.volatility * sqrt(3 * self.time_delta)  )

    @cached_property
    def div_step(self) -> float:
        if self.market.dividende <= 0:
            return -1
        else:
            time_delta_in_days = self.time_delta * 356
            return ceil((self.market.div_date - self.option.start_date).days/time_delta_in_days)

    @cached_property
    def exercise_steps(self) -> list[int]:

        if isinstance(self.option, BermudeanCallOption) or isinstance(self.option, BermudeanPutOption):
            exercise_dates = self.option.exercise_dates
            time_delta_in_days = self.time_delta * 356
            return [ceil((ex_date - self.option.start_date).days/time_delta_in_days) for ex_date in exercise_dates]
        
        elif isinstance(self.option, AmericanCallOption) or isinstance(self.option, AmericanPutOption):
            return [i for i in range(self.nb_steps)]
        
        else:
            return []

            
    def price_tree(self):

        self.root_node = Node(price = self.market.spot)
        mid_node = self.root_node
        
        #On  génère l'arbre avec seulement les noeuds mid
        for _ in range(self.nb_steps):
            mid_node.next_mid = mid_node.calculate_forward_node(self.market.rate, self.time_delta, self.market.dividende, False)
            mid_node.next_mid.prec_node = mid_node
            mid_node = mid_node.next_mid

        # On compute les prices et payoff sur le dernier noeud
        k =int(6*sqrt(self.nb_steps/3))
        self._compute_last_payoff(mid_node, k)
        
        for i in range(self.nb_steps-1,-1,-1):
            mid_node = mid_node.prec_node
            k = int(min(i, 6*sqrt(i/3)))
            self._compute_mid_node(mid_node, i)
            self._compute_upper_nodes(mid_node,k, i)
            self._compute_down_nodes(mid_node,k, i)

        return mid_node.payoff

    def _compute_last_payoff(self, node : Node, k : int):
        node.payoff = self.option.payoff(node.price)
        node_up  = node
        node_down = node
        
        for _ in range(k):
            node_down.down_node = Node(price = node_down.price / self.alpha)
            node_down.down_node.up_node = node_down
            node_down = node_down.down_node
            node_down.payoff = self.option.payoff(node_down.price)
        
        for _ in range(k):    
            node_up.up_node = Node(price = node_up.price * self.alpha)
            node_up.up_node.down_node = node_up
            node_up = node_up.up_node
            node_up.payoff = self.option.payoff(node_up.price)
    
    '''
    Permet de calculer les payoffs des noeuds du milieu
    '''
    def _compute_mid_node(self, node:Node, i:int):
        node.next_up = node.next_mid.up_node
        node.next_down = node.next_mid.down_node
        node.compute_proba(alpha = self.alpha, time_delta = self.time_delta, market = self.market, dividende = self.market.dividende, is_div = False)
        self._compute_retro_payoff(node, i)
        node.next_mid.next_mid = None
    
    '''
    Calcul des payoff des noeuds du haut
    '''
    def _compute_upper_nodes(self, node:Node,k:int, i:int):
        for _ in range(k):
            # On cree le noeud de haut dessus
            node.up_node = Node(price = node.price * self.alpha)
            node.up_node.down_node = node
            node = node.up_node
            # On relie 
            node.next_mid = node.down_node.next_up
            node.next_down = node.down_node.next_mid
            node.next_up = node.next_mid.up_node
            # On calcule les proba et les payoff
            if (node.next_up is None):
                node.p_mid = 1.0
                node.p_down = 0.0
                node.p_up = 0.0
            else:
                node.compute_proba(alpha = self.alpha, time_delta = self.time_delta, market = self.market, dividende = self.market.dividende, is_div = False)
            
            self._compute_retro_payoff(node, i)
            node.next_mid.next_mid = None

    def _compute_down_nodes(self, node:Node,k:int, i:int):
        for _ in range(k):
            # On cree le noeud de haut dessus
            node.down_node = Node(price = node.price / self.alpha)
            node.down_node.up_node = node
            node = node.down_node
            # On relie 
            node.next_mid = node.up_node.next_down
            node.next_up = node.up_node.next_mid
            node.next_down = node.next_mid.down_node
            # On calcule les proba et les payoff
            if (node.next_down is None):
                node.p_mid = 1.0
                node.p_down = 0.0
                node.p_up = 0.0
            else:
                node.compute_proba(alpha = self.alpha, time_delta = self.time_delta, market = self.market, dividende = self.market.dividende, is_div = False)

            self._compute_retro_payoff(node, i)
            node.next_mid.next_mid = None


    def _compute_retro_payoff(self, node : Node, step : int):
        if node.payoff is None:
            #Check if the node exists because of tree prunning
            value_up = node.next_up.payoff * node.p_up if node.next_up is not None else 0
            value_down = node.next_down.payoff * node.p_down if node.next_down is not None else 0
            value_mid = node.next_mid.payoff * node.p_mid if node.next_mid is not None else 0

            expectation = value_up + value_down + value_mid
            retro_payoff = expectation * exp(-self.market.rate * self.time_delta)

            if step in self.exercise_steps:
                exercise_payoff = self.option.payoff(node.price)
                node.payoff = max(retro_payoff, exercise_payoff)
            else:
                node.payoff = retro_payoff



    