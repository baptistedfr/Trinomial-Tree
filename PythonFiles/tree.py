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
        
    def generate_tree(self):

        self.root_node = Node(price = self.market.spot, node_proba = 1)
        mid_node = self.root_node

        for step in tqdm(range(self.nb_steps), total=self.nb_steps, desc="Building tree...", leave=False):
            is_div = True if step == self.div_step else False
            mid_node = self._build_column(mid_node, is_div)

        # for step in range(self.nb_steps):
        #     is_div = True if step == self.div_step else False
        #     mid_node = self._build_column(mid_node, is_div)

        self.last_node = mid_node
    
    def _build_column(self, mid_node : Node, is_div : bool):
        
        self._build_triplet(mid_node, is_div)

        upper_node = mid_node.up_node
        down_node = mid_node.down_node

        while down_node is not None:
            down_node = self._compute_down_nodes(down_node, is_div)
        while upper_node is not None:
            upper_node = self._compute_upper_nodes(upper_node, is_div)
            
        return mid_node.next_mid

    def _build_triplet(self, node : Node, is_div : bool):
        
        node.next_mid = node.calculate_forward_node(self.market.rate, self.time_delta, self.market.dividende, is_div)
        node.next_up = Node(price = node.next_mid.price * self.alpha)
        node.next_down = Node(price = node.next_mid.price / self.alpha)

        node.next_mid.down_node = node.next_down
        node.next_mid.up_node = node.next_up

        node.next_up.down_node = node.next_mid
        node.next_down.up_node = node.next_mid

        node.next_mid.prec_node = node

        node.compute_proba(self.alpha, self.time_delta, self.market, is_div, self.market.dividende)

        node.next_mid.node_proba = node.node_proba * node.p_mid
        node.next_up.node_proba = node.node_proba * node.p_up
        node.next_down.node_proba = node.node_proba * node.p_down

    def _find_mid_down(self, node : Node, candidate_mid : Node) -> Node:
        """Returns the next mid which is the closest to the forward price for down nodes computation"""

        forward_value = node.price * exp(self.market.rate * self.time_delta) - self.market.dividende

        while(True):
            down_price = candidate_mid.price / self.alpha

            average_price = (candidate_mid.price + down_price) / 2

            if forward_value > average_price:
                return candidate_mid
            else:
                future_mid_node = Node(price = down_price)
                future_mid_node.up_node = candidate_mid
                candidate_mid.down_node = future_mid_node

                candidate_mid = future_mid_node

    def _find_mid_up(self, node : Node, candidate_mid : Node) -> Node:
        """Returns the next mid which is the closest to the forward price for upper nodes computation"""

        forward_value = node.price * exp(self.market.rate * self.time_delta) - self.market.dividende

        while(True):
            up_price = candidate_mid.price * self.alpha

            average_price = (candidate_mid.price + up_price) / 2

            if forward_value < average_price:
                return candidate_mid
            else:
                future_mid_node = Node(price = up_price)
                future_mid_node.down_node = candidate_mid
                candidate_mid.up_node = future_mid_node

                candidate_mid = future_mid_node

    def _compute_upper_nodes(self, node : Node, is_div : bool) -> Node:
        if is_div:
            candidate_mid = node.down_node.next_up
            node.next_mid = self._find_mid_up(node, candidate_mid)
            node.next_down = node.next_mid.down_node
        else:
            node.next_mid = node.down_node.next_up
            node.next_down = node.down_node.next_mid

        if node.node_proba > self.prunning_value :
            #If no prunning : create next up node -> compute transition proba -> add node probabilities -> connect the new node
            node.next_up = Node(price = node.next_mid.price * self.alpha)

            node.compute_proba(self.alpha, self.time_delta, self.market, is_div, self.market.dividende)

            node.next_up.node_proba = node.next_up.node_proba + node.node_proba * node.p_up if node.next_up.node_proba is not None else node.node_proba * node.p_up
            node.next_mid.node_proba = node.next_mid.node_proba + node.node_proba * node.p_mid if node.next_mid.node_proba is not None else node.node_proba * node.p_mid
            node.next_down.node_proba = node.next_down.node_proba + node.node_proba * node.p_down if node.next_down.node_proba is not None else node.node_proba * node.p_down

            node.next_up.down_node = node.next_mid
            node.next_mid.up_node = node.next_up
            
            return node.up_node
        else :
            #If prunning : monomial branching = 100% proba mid
            node.p_mid = 1.0
            node.p_down = 0.0
            node.p_up = 0.0

            node.next_mid.node_proba += node.node_proba * node.p_mid
            return None

    def _compute_down_nodes(self, node : Node, is_div : bool):
        if is_div:
            candidate_mid = node.up_node.next_down
            node.next_mid = self._find_mid_down(node, candidate_mid)
            node.next_up = node.next_mid.up_node
        else:
            node.next_mid = node.up_node.next_down
            node.next_up = node.up_node.next_mid

        if node.node_proba > self.prunning_value :
            #If no prunning : create next up node -> compute transition proba -> add node probabilities -> connect the new node
            node.next_down = Node(price = node.next_mid.price / self.alpha)

            node.compute_proba(self.alpha, self.time_delta, self.market, is_div, self.market.dividende)

            node.next_up.node_proba = node.next_up.node_proba + node.node_proba * node.p_up if node.next_up.node_proba is not None else node.node_proba * node.p_up
            node.next_mid.node_proba = node.next_mid.node_proba + node.node_proba * node.p_mid if node.next_mid.node_proba is not None else node.node_proba * node.p_mid
            node.next_down.node_proba = node.next_down.node_proba + node.node_proba * node.p_down if node.next_down.node_proba is not None else node.node_proba * node.p_down

            node.next_down.up_node = node.next_mid
            node.next_mid.down_node = node.next_down

            return node.down_node
        else :
            #If prunning : monomial branching = 100% proba mid
            node.p_mid = 1.0
            node.p_down = 0.0
            node.p_up = 0.0

            node.next_mid.node_proba += node.node_proba * node.p_mid
            
            return None
    
    def _compute_final_payoff(self, trunc_node : Node):        
        end_node_down = trunc_node
        end_node_up = trunc_node

        while end_node_up is not None:
            end_node_up.payoff = self.option.payoff(end_node_up.price)
            end_node_up = end_node_up.up_node
            
        while end_node_down is not None:
            end_node_down.payoff = self.option.payoff(end_node_down.price)
            end_node_down = end_node_down.down_node
    
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

    def _retro_payoff(self, trunc_node : Node, step : int):
        
        this_up = trunc_node
        this_down = trunc_node
        while this_up is not None:
            self._compute_retro_payoff(this_up, step)
            this_up = this_up.up_node
        while this_down is not None:
            self._compute_retro_payoff(this_down, step)
            this_down =this_down.down_node

    def price(self):

        last_node = self.last_node
        self._compute_final_payoff(last_node)

        step = self.nb_steps - 1
        trunc_node = last_node.prec_node
        while trunc_node is not None:
            self._retro_payoff(trunc_node, step)
            trunc_node = trunc_node.prec_node
            step-=1