import ray

# Start Ray
ray.init()

#@ray.remote
class Account:
    def __init__(self, balance: float, minimal_balance: float):
        self.minimal = minimal_balance
        if balance < minimal_balance:
            raise Exception("Starting balance is less then minimal balance")
        self.balance = balance

    def balance(self) -> float:
        return self.balance

    def deposit(self, amount: float) -> float:
        if amount < 0:
            raise Exception("Can not deposit negative amount")
        self.balance = self.balance + amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount < 0:
            raise Exception("Can not withdraw negative amount")
        balance = self.balance - amount
        if balance < self.minimal:
            raise Exception("Withdraw is not supported by current balance")
        self.balance = balance
        return balance


Account = ray.remote(Account)
account_actor = Account.options(name='Account')\
    .remote(balance = 100.,minimal_balance=20.)


print(f"Current balance {ray.get(account_actor.balance.remote())}")
print(f"New balance {ray.get(account_actor.withdraw.remote(40.))}")
try:
    print(f"New balance {ray.get(account_actor.withdraw.remote(-40.))}")
except Exception as e:
    print(f"Oops! {e} occurred.")

print(f"New balance {ray.get(account_actor.deposit.remote(30.))}")

print(ray.get_actor('Account'))

ray.kill(account_actor)

print(ray.get_actor('Account'))
