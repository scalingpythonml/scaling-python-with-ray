import ray
from os.path import exists

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

    def save(self, key: str, data: dict):
        bytes = ray.cloudpickle.dumps(data)
        with open(self.basedir + '/' + key, "wb") as f:
            f.write(bytes)

    def restore(self, key:str) -> dict:
        with open(self.basedir + '/' + key, "rb") as f:
            bytes = f.read()
        return ray.cloudpickle.loads(bytes)

persistence_actor = FilePersistence.remote()

@ray.remote
class Account:
    def __init__(self, balance: float, minimal_balance: float, account_key: str, persistence):
        self.persistence = persistence
        self.key = account_key
        if ray.get(persistence.exists.remote(account_key)):
            # We have a state to restore
            self.restorestate()
        else:
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

    def restorestate(self):
        state = ray.get(self.persistence.restore.remote(self.key))
        self.balance = state['balance']
        self.minimal = state['minimal']

    def storestate(self):
        self.persistence.save.remote(self.key,
                                     {'balance' : self.balance, 'minimal' : self.minimal})

account_actor = Account.options(name='Account').remote(balance=100.,minimal_balance=20.,
                                    account_key='1234567', persistence=persistence_actor)


print(f"Current balance {ray.get(account_actor.balance.remote())}")
print(f"New balance {ray.get(account_actor.withdraw.remote(40.))}")
print(f"New balance {ray.get(account_actor.deposit.remote(70.))}")

print(ray.get_actor('Account'))

ray.kill(account_actor)

account_actor = Account.options(name='Account') .remote(balance=100.,minimal_balance=20.,
                                    account_key='1234567', persistence=persistence_actor)

print(f"Current balance {ray.get(account_actor.balance.remote())}")

