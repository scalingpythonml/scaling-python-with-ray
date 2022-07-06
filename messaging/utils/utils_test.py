# flake8: noqa: F841
import unittest
import ray

from . import utils


@ray.remote
class Bloop():
    """
    Bloop
    """


class UtilsTest(unittest.TestCase):
    """
    Test for the general utils.
    """
    @classmethod
    def setUpClass(cls):
        ray.init(num_cpus=4, num_gpus=0)

    @classmethod
    def tearDownClass(cls):
        ray.shutdown()

    def test_flatmap(self):
        self.assertEqual(
            [0, 0, 1, 0, 1, 2],
            utils.flat_map(lambda x: range(0, x), range(0, 4)))

    def basic_test_lazy_named_pool(self):
        actor = Bloop.options(name="basic_0").remote()
        lazy_pool = utils.LazyNamedPool("basic", 2)
        pool = lazy_pool.get_pool()
        self.assertEqual(len(lazy_pool._actors), 1)
        next_actor = Bloop.options(name="basic_1").remote()
        pool = lazy_pool.get_pool()
        self.assertEqual(len(lazy_pool._actors), 2)


if __name__ == "__main__":
    unittest.main()
