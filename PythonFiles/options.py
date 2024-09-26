from math import log, sqrt, exp
from datetime import datetime
from scipy.stats import norm
from PythonFiles.market import Market
from abc import ABC
import numpy as np
from dataclasses import dataclass


@dataclass
class Option(ABC):
        
    strike : float
    time_to_maturity : float
    start_date : datetime = None

    def d1(self, market) -> float:
        div_rate = market.dividende/market.spot
        return (log(market.spot/self.strike) + self.time_to_maturity * (market.rate - div_rate + (pow(market.volatility, 2)/2)))/(market.volatility * sqrt(self.time_to_maturity))

    def d2(self, market) -> float:
        return self.d1(market) - market.volatility*sqrt(self.time_to_maturity)
    
    
    def compute_price(self,market, n_sim=100000):
        Z = np.random.normal(0, 1, n_sim)
        prices = market.spot * np.exp(
            (market.rate - 0.5 * pow(market.volatility, 2)) * self.time_to_maturity +
            market.volatility * np.sqrt(self.time_to_maturity) * Z
        )
        payoffs=np.array([self.payoff(S) for S in prices])
        return exp(-market.rate*self.time_to_maturity) * np.mean(payoffs)

class CallOption(Option):
    
    def payoff(self, price : float) -> float:
        return max(0, (price - self.strike))
    
class PutOption(Option):
    def payoff(self, price : float) -> float:
        return max(0, (self.strike - price))

    
class EuropeanCallOption(CallOption):
    
    def compute_price(self, market) -> float:
        div_rate = market.dividende/market.spot
        return market.spot * exp(-div_rate * self.time_to_maturity) * norm.cdf(self.d1(market)) - self.strike * exp(-market.rate*self.time_to_maturity)*norm.cdf(self.d2(market))

class EuropeanPutOption(PutOption):
    
    def compute_price(self, market):
        div_rate = market.dividende/market.spot
        return -market.spot * exp(-div_rate * self.time_to_maturity) * norm.cdf(-self.d1(market)) + self.strike * exp(-market.rate*self.time_to_maturity)*norm.cdf(-self.d2(market))

class AmericanCallOption(CallOption):
    pass
    
class AmericanPutOption(PutOption):
    pass
    
class BermudeanCallOption(CallOption):
    exercise_dates : list[datetime]

class BermudeanPutOption(PutOption):
    exercise_dates : list[datetime]