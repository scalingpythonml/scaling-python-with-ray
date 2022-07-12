class FakeLazyNamedPool():
    def __init__(self, name, size, min_size=1):
        pass

    def get_pool(self):
        return FakePool()


class FakePool():
    def __init__(self):
        self.called = []

    def submit(self, *params):
        self.called.append(params)
        return True
