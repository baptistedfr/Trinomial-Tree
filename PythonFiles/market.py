from abc import ABC
from pydantic import BaseModel
from datetime import datetime

class Market(BaseModel):
    
    spot : float
    volatility : float
    rate : float
    dividende : float = 0
    div_date : datetime = None