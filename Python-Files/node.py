from pydantic import BaseModel, computed_field
from math import exp

class Node(BaseModel):
    
    price : float
    payoff : float = None
    
    next_up : 'Node' = None
    next_mid : 'Node' = None
    next_down : 'Node' = None
    up_node : 'Node' = None
    down_node : 'Node' = None
    prec_node : 'Node' = None
    
    def calculate_forward_node(self,rate:float,delta_time:float):
        forward_price=self.price*exp(rate*delta_time)
        return Node(price=forward_price)