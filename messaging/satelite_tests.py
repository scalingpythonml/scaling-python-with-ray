import unittest
import ray
import os
from . import test_utils

os.environ["hivebaseurl"] = "http://www.farts.com"

from . import satelite  # noqa: E402


class StandaloneSateliteTests(unittest.TestCase):
    def test_login_fails(self):
        s = satelite.SateliteClientBase(0, 1)
        self.assertRaises(Exception, s._login)


@ray.remote
class SateliteClientForTesting(satelite.SateliteClientBase):
    def __init__(self, idx, poolsize):
        satelite.SateliteClientBase.__init__(self, idx, poolsize)
        self.user_pool = test_utils.FakeLazyNamedPool("user", 1)


class RaySateliteTests(unittest.TestCase):
    """
    Test for the satelite magic.
    """
    @classmethod
    def setUpClass(cls):
        ray.init(num_cpus=4, num_gpus=0)

    @classmethod
    def tearDownClass(cls):
        ray.shutdown()

    def test_satelite_client_construct(self):
        mysatelite = satelite.SateliteClient.remote(0, 1)  # noqa: F841

    def test_satelite_client_test_construct(self):
        mysatelite = SateliteClientForTesting.remote(0, 1)  # noqa: F841
