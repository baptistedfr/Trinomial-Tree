from options import EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption
from pydantic import BaseModel, computed_field
from math import exp, sqrt, ceil
from typing import Union
from node import Node

class Tree(BaseModel):
   
    option : Union[EuropeanCallOption, EuropeanPutOption, AmericanCallOption, AmericanPutOption]
    nb_steps : int
    root_node : Node = None
    last_node : Node = None

    @computed_field
    @property
    def time_delta(self) -> float:
        return self.option.time_to_maturity / self.nb_steps    

    @computed_field
    @property
    def alpha(self) -> float:
        return exp(self.option.market.volatility * sqrt(3 * self.time_delta)  )
    
    @computed_field
    @property
    def div_step(self) -> float:
        time_delta_in_days = self.time_delta * 356
        return ceil((self.option.div_date - self.option.start_date).days/time_delta_in_days)
    
    def generate_tree(self):

        self.root_node = Node(price = self.option.market.spot)
        mid_node = self.root_node

        # for _ in tqdm(range(self.nb_steps-1), total=self.nb_steps-1, desc="Building tree...", leave=False):
        #     mid_node = self._build_column(mid_node)

        for step in range(self.nb_steps-1):
            is_div = True if step == self.div_step else False

            mid_node = self._build_column(mid_node, is_div)

        self.last_node = mid_node
    
    def _build_column(self, mid_node : Node, is_div : bool):
        
        self._build_triplet(mid_node, is_div)

        upper_node = mid_node.up_node
        down_node = mid_node.down_node

        while down_node != None and upper_node !=None:
            upper_node = self._compute_upper_nodes(upper_node)
            down_node = self._compute_down_nodes(down_node)
            
        return mid_node.next_mid

    def _build_triplet(self, node : Node, is_div : bool):
        
        node.next_mid = node.calculate_forward_node(self.option.market.rate, self.time_delta, self.option.dividende, is_div)
        node.next_up = Node(price = node.next_mid.price * self.alpha)
        node.next_down = Node(price = node.next_mid.price / self.alpha)

        node.next_mid.down_node = node.next_down
        node.next_mid.up_node = node.next_up

        node.next_up.down_node = node.next_mid
        node.next_down.up_node = node.next_mid

        node.next_mid.prec_node = node

    def _compute_upper_nodes(self,upper_node : Node):
        upper_node.next_mid = upper_node.down_node.next_up
        upper_node.next_down = upper_node.down_node.next_mid
        next_up_price = upper_node.next_mid.price * self.alpha
        upper_node.next_up = Node(price = next_up_price)

        upper_node.next_up.down_node = upper_node.next_mid
        upper_node.next_mid.up_node = upper_node.next_up

        return upper_node.up_node

    def _compute_down_nodes(self, down_node : Node):

        down_node.next_mid = down_node.up_node.next_down
        down_node.next_up = down_node.up_node.next_mid
        next_down_price = down_node.next_mid.price / self.alpha
        down_node.next_down = Node(price = next_down_price)

        down_node.next_down.up_node = down_node.next_mid
        down_node.next_mid.down_node = down_node.next_down

        return down_node.down_node
    
    def _compute_final_payoff(self, end_node_up : Node):
        """Price the last column according to the option payoff"""
        
        end_node_down = end_node_up
        while end_node_up is not None:
            end_node_up.payoff = self.option.payoff(end_node_up.price)
            end_node_down.payoff = self.option.payoff(end_node_down.price)
            end_node_up = end_node_up.up_node
            end_node_down = end_node_down.down_node
    
    def _compute_retro_payoff(self, node : Node):
        if node.payoff is None:
            node.compute_proba(self.alpha, self.time_delta, self.option)
            expectation = node.next_down.payoff * node.p_down + node.next_up.payoff * node.p_up + node.next_mid.payoff * node.p_mid  
            node.payoff = expectation * exp(-self.option.market.rate * self.time_delta)

    def _retro_payoff(self, trunc_node : Node):
        
        this_up = trunc_node
        this_down = trunc_node
        while this_up is not None:
            self._compute_retro_payoff(this_up)
            self._compute_retro_payoff(this_down)
            this_up = this_up.up_node
            this_down =this_down.down_node

    def price(self):

        last_node = self.last_node
        self._compute_final_payoff(last_node)

        trunc_node = last_node.prec_node
        while trunc_node is not None:
            self._retro_payoff(trunc_node)
            trunc_node = trunc_node.prec_node