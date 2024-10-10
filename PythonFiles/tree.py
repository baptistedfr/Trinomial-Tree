from PythonFiles.options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption
from math import exp, sqrt, ceil
from typing import Union
from PythonFiles.node import Node
from tqdm import tqdm
from dataclasses import dataclass
from functools import cached_property
from PythonFiles.market import Market

@dataclass
class Tree():
   
    option : Union[EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption, BermudeanCallOption, BermudeanPutOption]
    market : Market
    nb_steps : int
    root_node : Node = None
    last_node : Node = None
    
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
            time_delta_in_days = self.time_delta * 365
            return ceil((self.market.div_date - self.option.start_date).days/time_delta_in_days)

    @cached_property
    def exercise_steps(self) -> list[int]:

        if isinstance(self.option, BermudeanCallOption) or isinstance(self.option, BermudeanPutOption):
            exercise_dates = self.option.exercise_dates
            time_delta_in_days = self.time_delta * 365
            return [ceil((ex_date - self.option.start_date).days/time_delta_in_days) for ex_date in exercise_dates]
        
        elif isinstance(self.option, AmericanCallOption) or isinstance(self.option, AmericanPutOption):
            return [i for i in range(self.nb_steps)]
        
        else:
            return []
        
    def generate_tree(self):
        '''
        Fonction qui permet de générer l'abre colonne par colonne en calculant les probabilités 
        et en calculant les prix de chaque noeud
        '''
        self.root_node = Node(price = self.market.spot, node_proba = 1)
        mid_node = self.root_node

        # for step in tqdm(range(self.nb_steps), total=self.nb_steps, desc="Building tree...", leave=False):
        #     is_div = True if step == self.div_step else False
        #     mid_node = self._build_column(mid_node, is_div)

        for step in range(self.nb_steps):
            is_div = True if step == self.div_step else False
            mid_node = self._build_column(mid_node, is_div)

        self.last_node = mid_node
    
    def _build_column(self, mid_node : Node, is_div : bool):
        '''
        Fonction qui génere une colonne de noeud
        '''
        self._build_triplet(mid_node, is_div)

        upper_node = mid_node.up_node
        down_node = mid_node.down_node

        while down_node is not None:
            down_node = self._compute_down_nodes(down_node, is_div)
        while upper_node is not None:
            upper_node = self._compute_upper_nodes(upper_node, is_div)
            
        return mid_node.next_mid

    def _build_triplet(self, node : Node, is_div : bool):
        '''
        Génération des 3 noeuds principaux depuis le noeud central à chaque colonne
        '''
        node.next_mid = self.calculate_forward_node(node, is_div)
        node.next_up = Node(price = node.next_mid.price * self.alpha)
        node.next_down = Node(price = node.next_mid.price / self.alpha)

        node.branch_triplet()

        node.compute_transition_proba(self.alpha, self.time_delta, self.market, is_div, self.market.dividende)

        node.next_mid.node_proba = node.node_proba * node.p_mid
        node.next_up.node_proba = node.node_proba * node.p_up
        node.next_down.node_proba = node.node_proba * node.p_down

    def _find_mid(self, node: Node, candidate_mid: Node, direction: str) -> Node:
        """Returns the next mid node closest to the forward price for both up and down directions."""
        forward_value = node.price * exp(self.market.rate * self.time_delta) - self.market.dividende

        while True:
            if direction == "down":
                next_price = candidate_mid.price / self.alpha
                condition = forward_value > (candidate_mid.price + next_price) / 2
            else:
                next_price = candidate_mid.price * self.alpha
                condition = forward_value < (candidate_mid.price + next_price) / 2

            if condition:
                return candidate_mid
            else:
                future_mid_node = Node(price=next_price)
                if direction == "down":
                    future_mid_node.up_node = candidate_mid
                    candidate_mid.down_node = future_mid_node
                else:
                    future_mid_node.down_node = candidate_mid
                    candidate_mid.up_node = future_mid_node

                candidate_mid = future_mid_node
                

    def _compute_upper_nodes(self, node : Node, is_div : bool) -> Node:
        if is_div:
            candidate_mid = node.down_node.next_up
            node.next_mid = self._find_mid(node, candidate_mid, "up")
            node.next_down = node.next_mid.down_node
        else:
            node.next_mid = node.down_node.next_up
            node.next_down = node.down_node.next_mid

        if node.node_proba > self.prunning_value :
            #If no prunning : create next up node -> compute transition proba -> add node probabilities -> connect the new node
            node.next_up = Node(price = node.next_mid.price * self.alpha)

            node.compute_transition_proba(self.alpha, self.time_delta, self.market, is_div, self.market.dividende)
            node.update_proba()
            node.next_up.down_node = node.next_mid
            node.next_mid.up_node = node.next_up
            
            return node.up_node
        else :
            #If prunning : monomial branching = 100% proba mid
            node.compute_monomial()
            return None

    def _compute_down_nodes(self, node : Node, is_div : bool)-> Node:
        if is_div:
            candidate_mid = node.up_node.next_down
            node.next_mid = self._find_mid(node, candidate_mid, "down")
            node.next_up = node.next_mid.up_node
        else:
            node.next_mid = node.up_node.next_down
            node.next_up = node.up_node.next_mid

        #Si pas de prunning : on créer le noeud down fils et on calcule les proba
        if node.node_proba > self.prunning_value :
            node.next_down = Node(price = node.next_mid.price / self.alpha)

            #Calcul des proba de transition
            node.compute_transition_proba(self.alpha, self.time_delta, self.market, is_div, self.market.dividende)

            #Calcul des proba d'existance des noeuds fils
            node.update_proba()

            node.next_down.up_node = node.next_mid
            node.next_mid.down_node = node.next_down
            return node.down_node
        
        #Si prunning : branchement monomial
        else :
            node.compute_monomial()
            return None
    
    def calculate_forward_node(self, node : Node, is_div : bool):
        '''
        Calcul du forward en fonction du dividende
        '''
        if is_div:
            forward_price = node.price * exp(self.market.rate * self.time_delta) - self.market.dividende
        else :
            forward_price = node.price * exp(self.market.rate * self.time_delta)
        return Node(price = forward_price)

    def _compute_final_payoff(self, trunc_node : Node): 
        '''
        Calcule le payoff de l'option sur la dernière colonne
        '''       
        this_up = trunc_node
        this_down = trunc_node

        #Itération vers les noeuds supérieurs
        while this_up is not None:
            this_up.payoff = self.option.payoff(this_up.price)
            this_up = this_up.up_node
        
         #Itération vers les noeuds inférieurs
        while end_node_down is not None:
            end_node_down.payoff = self.option.payoff(end_node_down.price)
            end_node_down = end_node_down.down_node

    def _retro_payoff(self, trunc_node : Node, step : int) -> None:
        '''
        Calcule le prix de l'option sur la colonne par rétropropagation
        '''
        this_up = trunc_node
        this_down = trunc_node

        #Itération vers les noeuds supérieurs
        while this_up is not None:
            this_up.node_retro_payoff(step, self.option, self.exercise_steps, self.market.rate, self.time_delta)
            this_up = this_up.up_node

        #Itération vers les noeuds inférieurs
        while this_down is not None:
            this_down.node_retro_payoff(step, self.option, self.exercise_steps, self.market.rate, self.time_delta)
            this_down =this_down.down_node

    def price(self) -> None:
        '''
        Pricer l'option avec l'arbre par mouvement backward
        '''
        last_node = self.last_node
        #Calcul du payoff de la dernière colonne
        self._compute_final_payoff(last_node)

        step = self.nb_steps - 1
        trunc_node = last_node.prec_node

        #Itération sur les noeuds du tronc en backward
        while trunc_node is not None:
            self._retro_payoff(trunc_node, step)
            trunc_node = trunc_node.prec_node
            step-=1