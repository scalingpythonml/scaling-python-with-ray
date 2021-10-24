import ray

# Start Ray
ray.init()

#@ray.remote
class Account:
    def __init__(self, balance: float, minimal_balance: float):
        if balance < minimal_balance:
            print(f"Balance {balance} is less then minimal balance {minimal_balance}")
            raise Exception("Starting balance is less then minimal balance")
        self.balance = balance
        self.minimal = minimal_balance

    def balance(self) -> float:
        return self.balance

    def deposit(self, amount: float) -> float:
        if amount < 0:
            print(f"Can not deposit negative amount {amount} ")
            raise Exception("Can not deposit negative amount")
        self.balance = self.balance + amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        balance = self.balance - amount
        if balance < self.minimal:
            print(f"Withdraw amount {amount} is too large for a current balance {self.balance}")
            raise Exception("Withdraw is not supported by current balance")
        self.balance = balance
        return balance

Account = ray.remote(Account)
account_actor = Account.options(name='Account')\
    .remote(balance = 100.,minimal_balance=20.)


print(f"Current balance {ray.get(account_actor.balance.remote())}")
print(f"New balance {ray.get(account_actor.withdraw.remote(40.))}")
print(f"New balance {ray.get(account_actor.deposit.remote(30.))}")

print(ray.get_actor('Account'))

ray.kill(account_actor)

print(ray.get_actor('Account'))
