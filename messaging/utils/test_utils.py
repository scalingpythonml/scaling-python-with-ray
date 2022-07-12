class FakeLazyNamedPool():
    def __init__(self, name, size, min_size=1):
        self.pool = FakePool()
        pass

    def get_pool(self):
        return self.pool


class FakePool():
    submitted: list = []

    def submit(self, *params):
        self.submitted.append(params)
        return True
