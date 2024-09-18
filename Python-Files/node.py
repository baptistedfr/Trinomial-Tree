from pydantic import BaseModel, computed_field

class Node(BaseModel):
    
    price : float
    payoff : float = None
    
    next_up : 'Node' = None
    next_mid : 'Node' = None
    next_down : 'Node' = None
    up_node : 'Node' = None
    down_node : 'Node' = None