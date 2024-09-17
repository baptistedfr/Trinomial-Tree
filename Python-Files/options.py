from abc import ABC
from pydantic import BaseModel, computed_field
from math import log, sqrt, exp
from scipy.stats import norm
from datetime import datetime
from market import Market
import numpy as np
import random

class Option(ABC, BaseModel):
    
    market : Market
    strike : float
    time_to_maturity : float
    start_date : datetime = None

    @computed_field
    @property
    def d1(self) -> float:
        div_rate = self.market.dividende/self.market.spot
        return (log(self.market.spot/self.strike) + self.time_to_maturity * (self.market.rate - div_rate + (pow(self.market.volatility, 2)/2)))/(self.market.volatility * sqrt(self.time_to_maturity))
    
    @computed_field
    @property
    def d2(self) -> float:
        return self.d1 - self.market.volatility*sqrt(self.time_to_maturity)
    
    
    def compute_MC(self,n_sim):
        Z = np.random.normal(0, 1, n_sim)
        prices = self.market.spot * np.exp(
            (self.market.rate - 0.5 * pow(self.market.volatility, 2)) * self.time_to_maturity +
            self.market.volatility * np.sqrt(self.time_to_maturity) * Z
        )
        payoffs=np.array([self.payoff(S) for S in prices])
        return exp(-self.market.rate*self.time_to_maturity) * np.mean(payoffs)

class CallOption(Option):
    
    def payoff(self, price : float) -> float:
        return max(0, (price - self.strike))
    
class PutOption(Option):
    def payoff(self, price : float) -> float:
        return max(0, (self.strike - price))

    
class EuropeanCallOption(CallOption):
    
    def compute_BS(self) -> float:
        div_rate = self.market.dividende/self.market.spot
        return self.market.spot * exp(-div_rate * self.time_to_maturity) * norm.cdf(self.d1) - self.strike * exp(-self.market.rate*self.time_to_maturity)*norm.cdf(self.d2)

class EuropeanPutOption(PutOption):
    
    def compute_BS(self):
        div_rate = self.market.dividende/self.market.spot
        return -self.market.spot * exp(-div_rate * self.time_to_maturity) * norm.cdf(-self.d1) + self.strike * exp(-self.market.rate*self.time_to_maturity)*norm.cdf(-self.d2)

class AmericanCallOption(CallOption):
    pass
    
class AmericanPutOption(PutOption):
    pass
    
class BermudeanCallOption(CallOption):
    exercise_dates : list[datetime]

class BermudeanPutOption(PutOption):
    exercise_dates : list[datetime]





