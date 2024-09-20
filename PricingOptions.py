import xlwings as xw
from option import CallOption, PutOption
from tree import Tree
from abc import ABC,abstractmethod
from math import log,sqrt,exp,floor
from re import T
from scipy.stats import norm
import xlwings as xw
import time

def main():
    wb = xw.Book.caller()
    sheet_pricer = wb.sheets["Pricer"]
    type_option: str = sheet_pricer.range("OptionType").value
    exercise_type: float = sheet_pricer.range('ExerciceType').value
    initial_price: float = sheet_pricer.range('IntialPrice').value
    strike: float = sheet_pricer.range('Strike').value
    volatility: float = sheet_pricer.range('Volatility').value
    maturity: float = sheet_pricer.range('Maturity').value
    risk_free_rate: float = sheet_pricer.range('InterestRate').value

    nb_steps: float = sheet_pricer.range('NbSteps').value
    is_american: bool = False
    if (exercise_type == "US"):
        is_american = True
    
    if type_option == "Call":
        option = CallOption(spot=initial_price, strike=strike, risk_free_rate=risk_free_rate, time_to_maturity=maturity, volatility=volatility, is_american=is_american)
    else:
        option=PutOption(spot=initial_price, strike=strike, risk_free_rate=risk_free_rate, time_to_maturity=maturity, volatility=volatility, is_american=is_american)
    
    start_time = time.time()
    tree = Tree(option=option, nb_steps=nb_steps)
    tree.generate_tree()
    option_price = tree.price_tree()
    exec_time = time.time() - start_time

    sheet_pricer.range("PyBSPrice").value = option.bs_price()
    sheet_pricer.range("PyTreePrice").value = option_price  # Fix the method call here
    sheet_pricer.range("PyExecutionTime").value = exec_time
    
if __name__ == "__main__":
    xw.Book.caller().set_mock_caller()
    main()