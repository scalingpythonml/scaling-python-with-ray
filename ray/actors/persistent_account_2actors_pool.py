import ray
from os.path import exists
from ray.util import ActorPool


# Start Ray
ray.init()

class BasePersitence:
    def exists(self, key:str) -> bool:
        pass
    def save(self, key: str, data: dict):
        pass
    def restore(self, key:str) -> dict:
        pass

@ray.remote
class FilePersistence(BasePersitence):
    def __init__(self, basedir: str = '.'):
        self.basedir = basedir

    def exists(self, key:str) -> bool:
        return exists(self.basedir + '/' + key)

    def save(self, keyvalue: ()):
        bytes = ray.cloudpickle.dumps(keyvalue[1])
        with open(self.basedir + '/' + keyvalue[0], "wb") as f:
            f.write(bytes)

    def restore(self, key:str) -> dict:
        with open(self.basedir + '/' + key, "rb") as f:
            bytes = f.read()
        return ray.cloudpickle.loads(bytes)

pool = ActorPool([FilePersistence.remote(), FilePersistence.remote(), FilePersistence.remote()])

@ray.remote
class Account:
    def __init__(self, balance: float, minimal_balance: float, account_key: str, persistence: ActorPool):
        self.persistence = persistence
        self.key = account_key
        if not self.restorestate():
            if balance < minimal_balance:
                print(f"Balance {balance} is less then minimal balance {minimal_balance}")
                raise Exception("Starting balance is less then minimal balance")
            self.balance = balance
            self.minimal = minimal_balance
            self.storestate()

    def balance(self) -> float:
        return self.balance

    def deposit(self, amount: float) -> float:
        self.balance = self.balance + amount
        self.storestate()
        return self.balance

    def withdraw(self, amount: float) -> float:
        balance = self.balance - amount
        if balance < self.minimal:
            print(f"Withdraw amount {amount} is too large for a current balance {self.balance}")
            raise Exception("Withdraw is not supported by current balance")
        self.balance = balance
        self.storestate()
        return balance

    def restorestate(self) -> bool:
        while(self.persistence.has_next()):
            pass
        self.persistence.submit(lambda a, v: a.exists.remote(v), self.key)
        if self.persistence.get_next():
            # We have a state to restore
            self.persistence.submit(lambda a, v: a.restore.remote(v), self.key)
            state = self.persistence.get_next()
            self.balance = state['balance']
            self.minimal = state['minimal']
            return True
        else:
            return False

    def storestate(self):
        self.persistence.submit(lambda a, v: a.save.remote(v), (self.key,
                                    {'balance' : self.balance, 'minimal' : self.minimal}))


account_actor = Account.options(name='Account').remote(balance=100.,minimal_balance=20.,
                                    account_key='1234567', persistence=pool)


print(f"Current balance {ray.get(account_actor.balance.remote())}")
print(f"New balance {ray.get(account_actor.withdraw.remote(40.))}")
print(f"New balance {ray.get(account_actor.deposit.remote(70.))}")

print(ray.get_actor('Account'))

ray.kill(account_actor)

account_actor = Account.options(name='Account') .remote(balance=100.,minimal_balance=20.,
                                    account_key='1234567', persistence=pool)

print(f"Current balance {ray.get(account_actor.balance.remote())}")

