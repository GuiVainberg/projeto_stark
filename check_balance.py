import starkbank
from stark_client import project

starkbank.user = project
balance = starkbank.balance.get()
print(balance)