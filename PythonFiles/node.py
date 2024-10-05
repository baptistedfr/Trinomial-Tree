from math import exp
from dataclasses import dataclass
from PythonFiles.market import Market

@dataclass
class Node():
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

    node_proba : float = 0
    
    def calculate_forward_node(self, rate : float, delta_time : float, dividende : float, is_div : bool):
        if is_div:
            forward_price = self.price * exp(rate * delta_time) - dividende
        else :
            forward_price = self.price * exp(rate * delta_time)
        return Node(price=forward_price)
    
    def compute_proba(self, alpha : float, time_delta : int, market : Market, is_div : bool, dividende : float):

        # next_mid_price = self.next_mid.price
        
        forward = self.next_mid.price
        if is_div:
             expectation = self.price * exp(market.rate * time_delta) - dividende
        else :
            expectation = self.next_mid.price
        variance = pow(self.price,2) * exp(2 * market.rate * time_delta) * (exp(pow(market.volatility, 2) * time_delta) -1) 
        
        self.p_down = ((pow(forward,-2) * (variance + pow(expectation,2)))- 1 - ((alpha+1) * ((pow(forward, -1)*expectation)-1))) / ((1 - alpha) * (pow(alpha,-2) - 1))
        self.p_up = ((pow(forward,-1)*expectation)-1-((alpha**(-1)-1)*self.p_down))/(alpha-1)
        self.p_mid = 1 - self.p_down - self.p_up