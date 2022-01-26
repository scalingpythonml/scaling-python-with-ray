import ray
from os.path import exists

# Start Ray
ray.init()

@ray.remote
class Account:
    def __init__(self, balance: float, minimal_balance: float, account_key: str, basedir: str = '.'):
        self.basedir = basedir
        self.key = account_key
        if not self.restorestate():
            if balance < minimal_balance:
                raise Exception("Starting balance is less then minimal balance")
            self.balance = balance
            self.minimal = minimal_balance
            self.storestate()

    def balance(self) -> float:
        return self.balance

    def deposit(self, amount: float) -> float:
        if amount < 0:
            raise Exception("Can not deposit negative amount")
        self.balance = self.balance + amount
        self.storestate()
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount < 0:
            raise Exception("Can not withdraw negative amount")
        balance = self.balance - amount
        if balance < self.minimal:
            raise Exception("Withdraw is not supported by current balance")
        self.balance = balance
        self.storestate()
        return balance

    def restorestate(self) -> bool:
        if exists(self.basedir + '/' + self.key):
            with open(self.basedir + '/' + self.key, "rb") as f:
                bytes = f.read()
            state = ray.cloudpickle.loads(bytes)
            self.balance = state['balance']
            self.minimal = state['minimal']
            return True
        else:
            return False

    def storestate(self):
        bytes = ray.cloudpickle.dumps({'balance' : self.balance, 'minimal' : self.minimal})
        with open(self.basedir + '/' + self.key, "wb") as f:
            f.write(bytes)

account_actor = Account.options(name='Account')\
    .remote(balance=100.,minimal_balance=20., account_key='1234567')


print(f"Current balance {ray.get(account_actor.balance.remote())}")
print(f"New balance {ray.get(account_actor.withdraw.remote(40.))}")
print(f"New balance {ray.get(account_actor.deposit.remote(70.))}")

print(ray.get_actor('Account'))

ray.kill(account_actor)

account_actor = Account.options(name='Account') \
    .remote(balance=100.,minimal_balance=20., account_key='1234567')

print(f"Current balance {ray.get(account_actor.balance.remote())}")

