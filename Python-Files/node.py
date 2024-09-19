from pydantic import BaseModel
from options import Option
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

    p_down : float = None
    p_up : float = None
    p_mid : float = None
    
    def calculate_forward_node(self, rate : float, delta_time : float, dividende : float, is_div : bool):
        if is_div:
            forward_price = self.price * exp(rate * delta_time) - dividende
        else :
            forward_price = self.price * exp(rate * delta_time)
        return Node(price=forward_price)
    
    def compute_proba(self, alpha : float, time_delta : int, option : Option):

        next_mid_price = self.next_mid.price
        variance = pow(self.price,2) * exp(2 * option.market.rate * time_delta) * (exp(pow(option.market.volatility, 2) * time_delta) -1) 
        expectation = self.next_mid.price

        self.p_down = ((pow(next_mid_price,-2) * (variance + pow(expectation,2)))- 1 - ((alpha+1) * ((pow(next_mid_price, -1)*expectation)-1))) / ((1 - alpha) * (pow(alpha,-2) - 1))
        self.p_up = ((pow(next_mid_price,-1)*expectation)-1-((alpha**(-1)-1)*self.p_down))/(alpha-1)

        # self.p_down = (exp(time_delta * pow(vol, 2)) - 1) / ((1-alpha) * (pow(alpha, -2) - 1))
        # self.p_up = self.p_down / alpha
        self.p_mid = 1 - self.p_down - self.p_up