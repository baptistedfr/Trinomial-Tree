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