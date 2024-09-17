from pydantic import BaseModel, computed_field
from math import exp, sqrt
from node import Node
from options import EuropeanCallOption, EuropeanPutOption
from typing import Union

class Tree(BaseModel):
   
   option : Union[EuropeanCallOption, EuropeanPutOption]
   nb_steps : int
   root_node : Node = None

   @computed_field
   @property
   def time_delta(self) -> float:
        return self.option.time_to_maturity / self.nb_steps

   @computed_field
   @property
   def alpha(self) -> float:
        return exp(self.option.market.volatility * sqrt(3 * self.time_delta))
   
   def build_tree(self):
       self.root_node = Node(price=self.option.market.spot)
       this_step_node = self.root_node
       for step in range(1, self.nb_steps):
           self.build_column(step, this_step_node)
       
   def build_column(self, step : int, this_step_node : Node):
        self.build_triplet(this_step_node)

   def build_triplet(self, this_node : Node):
       
    #    if candidate_mid is None:
    #        candidate_mid = Node(price=previous_node.price * exp(self.market.rate * self.delta_time))
           
    #    previous_node.next_mid = candidate_mid

    #    if candidate_mid.down_node is None:
    #     previous_node.next_up = Node()

        mid = Node(price=this_node.price * exp(self.option.market.rate * self.time_delta))
        up = Node(price=mid.price / self.alpha)
        down = Node(price=mid.price * self.alpha)

        this_node.next_down = down
        this_node.next_mid = mid
        this_node.next_up = up